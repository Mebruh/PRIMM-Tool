import json

from django.test import TestCase
from django.urls import reverse

from .executor import QueryExecutor
from .models import CustomQuestionSet
from .query_configs import BUILTIN_QUESTION_SETS
from .validators import QueryComparator


SET_API = '/api/question-set/cs209-1/'


def post_query(client, url, query):
    response = client.post(url, data=json.dumps({'query': query}), content_type='application/json')
    return response.json()


class DatabasePageTests(TestCase):
    def test_chooser_links_to_both_databases(self):
        response = self.client.get(reverse('databases'))
        self.assertContains(response, 'Company Database')
        self.assertContains(response, 'Store Database')
        self.assertContains(response, reverse('database-view'))
        self.assertContains(response, reverse('database-store'))

    def test_old_database_url_redirects_to_chooser(self):
        response = self.client.get('/database/')
        self.assertRedirects(response, reverse('databases'))

    def test_company_page_loads(self):
        self.assertContains(self.client.get(reverse('database-view')), 'Employees Table')

    def test_store_page_shows_every_table(self):
        response = self.client.get(reverse('database-store'))
        for table in ['customer', 'store', 'product', 'shoppinglist', 'purchase', 'inventory']:
            self.assertContains(response, f'<code>{table}</code>')
        self.assertContains(response, 'Mila')
        self.assertContains(response, 'Stationsplein')

    def test_navbar_says_view_databases(self):
        self.assertContains(self.client.get(reverse('home')), 'View Databases')


class StoreDataTests(TestCase):
    def test_store_tables_are_populated(self):
        expected_counts = {
            'customer': 5, 'store': 5, 'product': 5,
            'shoppinglist': 3, 'purchase': 4, 'inventory': 4,
        }
        for table, count in expected_counts.items():
            ok, result = QueryExecutor.execute_query(f'SELECT COUNT(*) AS n FROM {table}')
            self.assertTrue(ok)
            self.assertEqual(result[0]['n'], count, table)


class ProductTableTests(TestCase):
    def test_product_has_no_suffix_column(self):
        ok, result = QueryExecutor.execute_query('SELECT * FROM product')
        self.assertTrue(ok)
        self.assertEqual(list(result[0].keys()), ['pID', 'pName'])

    def test_store_page_has_no_suffix_column(self):
        self.assertNotContains(self.client.get(reverse('database-store')), 'suffix')

    def test_tables_still_join_to_product(self):
        ok, result = QueryExecutor.execute_query(
            'SELECT p.pName FROM purchase t JOIN product p ON t.pID = p.pID'
        )
        self.assertTrue(ok)
        self.assertEqual(len(result), 4)


class ExecutorTests(TestCase):
    def test_repeated_column_names_are_kept(self):
        ok, result = QueryExecutor.execute_query(
            'SELECT c1.cID, c2.cID FROM customer c1 JOIN customer c2 ON c1.cID = c2.cID WHERE c1.cID = 0'
        )
        self.assertTrue(ok)
        self.assertEqual(len(result[0]), 2)


class ComparatorTests(TestCase):
    def test_column_names_are_ignored_when_positions_match(self):
        self.assertTrue(QueryComparator.results_match([{'a': 1, 'b': 2}], [{'x': 1, 'y': 2}]))

    def test_column_order_is_ignored_when_names_match(self):
        self.assertTrue(QueryComparator.results_match([{'a': 1, 'b': 2}], [{'b': 2, 'a': 1}]))

    def test_different_rows_do_not_match(self):
        self.assertFalse(QueryComparator.results_match([{'a': 1}], [{'a': 2}]))
        self.assertFalse(QueryComparator.results_match([{'a': 1}], [{'a': 1}, {'a': 1}]))


class CS209Set1Tests(TestCase):
    def test_page_loads(self):
        response = self.client.get(reverse('cs209-1'))
        self.assertContains(response, 'CS209 Question Set 1')
        self.assertContains(response, reverse('database-store'))
        self.assertContains(response, SET_API)

    def test_predict_query_returns_self_matches_and_both_orders(self):
        result = self.client.get(SET_API + 'run-predict/').json()['result']
        pairs = sorted(tuple(row.values())[:2] for row in result)
        self.assertEqual(pairs, [(0, 0), (0, 4), (1, 1), (2, 2), (3, 3), (4, 0), (4, 4)])

    def test_modify_accepts_not_equal_and_less_than(self):
        base = 'SELECT c1.cID, c2.cID, c1.street FROM customer c1 JOIN customer c2 ON c1.street = c2.street '
        for condition in ['WHERE c1.cID <> c2.cID', 'WHERE c1.cID != c2.cID', 'WHERE c1.cID < c2.cID',
                          'AND c1.cID <> c2.cID']:
            data = post_query(self.client, SET_API + 'run-modify/', base + condition)
            self.assertTrue(data['correct'], condition)

    def test_modify_rejects_unchanged_query(self):
        data = post_query(self.client, SET_API + 'run-modify/', BUILTIN_QUESTION_SETS['cs209-1'].modify_initial_query)
        self.assertFalse(data['correct'])

    def test_make_accepts_model_answer_and_variations(self):
        answers = [
            BUILTIN_QUESTION_SETS['cs209-1'].make_correct_query,
            'select a.cid, b.cid from customer a join customer b on a.street = b.street '
            'where a.city != b.city and a.cid < b.cid',
            'SELECT c1.cID AS first, c2.cID AS second FROM customer c1, customer c2 '
            'WHERE c1.street = c2.street AND c1.city <> c2.city AND c2.cID > c1.cID;',
        ]
        for answer in answers:
            self.assertTrue(post_query(self.client, SET_API + 'run-make/', answer)['correct'], answer)

    def test_make_gives_hint_for_duplicate_pairs(self):
        data = post_query(
            self.client, SET_API + 'run-make/',
            'SELECT c1.cID, c2.cID FROM customer c1 JOIN customer c2 ON c1.street = c2.street '
            'WHERE c1.city <> c2.city',
        )
        self.assertFalse(data['correct'])
        self.assertIn('listed twice', data['hint'])

    def test_make_gives_hint_for_missing_city_check(self):
        data = post_query(
            self.client, SET_API + 'run-make/',
            'SELECT c1.cID, c2.cID FROM customer c1 JOIN customer c2 ON c1.street = c2.street',
        )
        self.assertIn('cities', data['hint'])

    def test_make_blocks_unsafe_queries(self):
        data = post_query(self.client, SET_API + 'run-make/', 'DROP TABLE customer')
        self.assertFalse(data['correct'])
        self.assertIn('error', data)

    def test_unknown_builtin_set_is_404(self):
        self.assertEqual(self.client.get('/api/question-set/nope/run-predict/').status_code, 404)


class CustomQuestionSetTests(TestCase):
    form_data = {
        'name': 'Store prices',
        'predict_query': 'SELECT pName FROM product',
        'predict_option1': 'a', 'predict_option2': 'b', 'predict_option3': 'c', 'predict_option4': 'd',
        'predict_correct_answer': '1',
        'investigate_q1': 'q1', 'investigate_a1': 'a1',
        'investigate_q2': 'q2', 'investigate_a2': 'a2',
        'investigate_q3': 'q3', 'investigate_a3': 'a3',
        'modify_task': 'Show store names', 'modify_initial_query': 'SELECT sID FROM store',
        'modify_correct_query': 'SELECT sName FROM store',
        'make_task': 'Count customers', 'make_correct_query': 'SELECT COUNT(*) FROM customer',
    }

    def test_form_offers_both_databases(self):
        response = self.client.get(reverse('add-question-set'))
        self.assertContains(response, 'value="company"')
        self.assertContains(response, 'value="store"')
        self.assertContains(response, 'value="inventory"')

    def test_create_store_question_set(self):
        data = dict(self.form_data, database='store', tables=['product', 'store', 'employees'])
        response = self.client.post(reverse('add-question-set'), data)
        self.assertRedirects(response, reverse('all-questions'))

        question_set = CustomQuestionSet.objects.get(name='Store prices')
        self.assertEqual(question_set.database, 'store')
        # employees is not a Store table, so it is dropped
        self.assertEqual(question_set.table_list, ['product', 'store'])

        page = self.client.get(reverse('custom-question-set', args=[question_set.pk]))
        self.assertContains(page, 'Store Database')
        self.assertContains(page, reverse('database-store'))

        api = f'/api/custom-question/{question_set.pk}/'
        self.assertEqual(len(self.client.get(api + 'run-predict/').json()['result']), 5)
        self.assertTrue(post_query(self.client, api + 'run-modify/', 'SELECT sName FROM store;')['correct'])
        self.assertTrue(post_query(self.client, api + 'run-make/', 'SELECT COUNT(cID) FROM customer')['correct'])
        self.assertFalse(post_query(self.client, api + 'run-make/', 'SELECT COUNT(*) FROM shoppinglist')['correct'])

        listing = self.client.get(reverse('all-questions'))
        self.assertContains(listing, 'Tables: product, store')

    def test_unknown_database_falls_back_to_company(self):
        self.client.post(reverse('add-question-set'), dict(self.form_data, database='nope'))
        self.assertEqual(CustomQuestionSet.objects.get(name='Store prices').database, 'company')


class ExistingQuestionSetTests(TestCase):
    """The original question sets should behave as before."""

    def test_pages_load(self):
        for name in ['primm1', 'primm2', 'primm3', 'all-questions', 'add-question-set']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_old_primm4_url_redirects(self):
        self.assertRedirects(self.client.get('/primm4/'), reverse('cs209-1'))


class SectionTests(TestCase):
    form_data = dict(CustomQuestionSetTests.form_data, database='store', tables=['store'])

    def page_sections(self):
        """Split the All Questions page into its CS209, Built-in and Custom parts."""
        html = self.client.get(reverse('all-questions')).content.decode()
        cs209_at = html.index('<!-- CS209 Question Sets -->')
        builtin_at = html.index('<!-- Built-in Question Sets -->')
        custom_at = html.index('<!-- Custom Question Sets -->')
        return html[cs209_at:builtin_at], html[builtin_at:custom_at], html[custom_at:]

    def test_cs209_section_is_above_built_in(self):
        cs209, builtin, _ = self.page_sections()
        self.assertIn('CS209 Question Set 1', cs209)
        self.assertIn(reverse('cs209-1'), cs209)
        self.assertNotIn('CS209 Question Set 1', builtin)
        self.assertNotIn('Question Set 4', builtin)

    def test_form_offers_both_sections(self):
        response = self.client.get(reverse('add-question-set'))
        self.assertContains(response, 'value="custom"')
        self.assertContains(response, 'value="cs209"')

    def test_set_appears_in_chosen_section(self):
        self.client.post(reverse('add-question-set'), dict(self.form_data, name='Lab 2', section='cs209'))
        self.client.post(reverse('add-question-set'), dict(self.form_data, name='My practice', section='custom'))

        cs209, builtin, custom = self.page_sections()
        self.assertIn('Lab 2', cs209)
        self.assertNotIn('Lab 2', custom)
        self.assertIn('My practice', custom)
        self.assertNotIn('My practice', cs209)
        self.assertNotIn('Lab 2', builtin)

    def test_missing_or_unknown_section_goes_to_custom(self):
        self.client.post(reverse('add-question-set'), dict(self.form_data, name='No section'))
        self.client.post(reverse('add-question-set'), dict(self.form_data, name='Bad section', section='nope'))
        for name in ['No section', 'Bad section']:
            self.assertEqual(CustomQuestionSet.objects.get(name=name).section, 'custom')

    def test_cs209_set_page_says_cs209(self):
        self.client.post(reverse('add-question-set'), dict(self.form_data, name='Lab 2', section='cs209'))
        question_set = CustomQuestionSet.objects.get(name='Lab 2')
        page = self.client.get(reverse('custom-question-set', args=[question_set.pk]))
        self.assertContains(page, 'CS209 PRIMM question set.')


class NextSetAndOrderingTests(TestCase):
    form_data = dict(CustomQuestionSetTests.form_data, database='store', tables=['store'])

    def create(self, name, section):
        self.client.post(reverse('add-question-set'), dict(self.form_data, name=name, section=section))
        return CustomQuestionSet.objects.get(name=name)

    def set_page(self, question_set):
        return self.client.get(reverse('custom-question-set', args=[question_set.pk]))

    def test_cs209_chain_runs_in_creation_order(self):
        lab2 = self.create('Lab 2', 'cs209')
        practice = self.create('Practice', 'custom')
        lab3 = self.create('Lab 3', 'cs209')

        # CS209 Question Set 1 -> Lab 2 (skipping the custom set) -> Lab 3 -> All Questions
        first = self.client.get(reverse('cs209-1'))
        self.assertContains(first, 'Up next: Lab 2')
        self.assertContains(first, reverse('custom-question-set', args=[lab2.pk]))

        self.assertContains(self.set_page(lab2), 'Up next: Lab 3')
        self.assertContains(self.set_page(lab2), reverse('custom-question-set', args=[lab3.pk]))

        last = self.set_page(lab3)
        self.assertNotContains(last, 'Up next')
        self.assertContains(last, 'Please remember to return to the survey.')
        self.assertNotContains(last, 'You have finished every question set in this section.')

        # The only custom set is last in its section
        self.assertNotContains(self.set_page(practice), 'Up next')

    def test_custom_chain(self):
        first = self.create('Custom A', 'custom')
        second = self.create('Custom B', 'custom')
        self.assertContains(self.set_page(first), 'Up next: Custom B')
        last = self.set_page(second)
        self.assertNotContains(last, 'Up next')
        self.assertContains(last, 'You have finished every question set in this section.')
        self.assertNotContains(last, 'return to the survey')

    def test_cs209_set_1_alone_is_last(self):
        page = self.client.get(reverse('cs209-1'))
        self.assertNotContains(page, 'Up next')
        self.assertContains(page, 'Please remember to return to the survey.')

    def test_sets_are_listed_oldest_first(self):
        for name in ['Zebra', 'Apple', 'Mango']:
            self.create(name, 'custom')
        html = self.client.get(reverse('all-questions')).content.decode()
        self.assertLess(html.index('Zebra'), html.index('Apple'))
        self.assertLess(html.index('Apple'), html.index('Mango'))

    def test_no_create_buttons_on_all_questions(self):
        html = self.client.get(reverse('all-questions')).content.decode()
        body = html[html.index('All Question Sets'):]
        self.assertNotIn(reverse('add-question-set'), body)
        # The navbar link to create a set is still there
        self.assertIn(reverse('add-question-set'), html)