# spese/tests.py
''' app spese tests
    run using: ``manage.py test spese.tests``
    ldfa@2016.12.06 1st (very) incomplete draft
'''
import pdb

from django.test import TestCase, Client

from django.core.urlresolvers import reverse, resolve
from django.db.models import Q
from django.contrib.auth.models import User

from spese.models import Expense, Account, TransferFund

class SpeseUrlsTestCase(TestCase):
    def test_urls(self):
        url = reverse('spese:index')
        self.assertEqual(url, '/spese/')
        url = reverse('spese:detail', args=[19])
        self.assertEqual(url, '/spese/19/')
        url = reverse('spese:add')
        self.assertEqual(url, '/spese/add/')
        url = reverse('spese:transfer_funds')
        self.assertEqual(url, '/spese/transfer_funds/')
        url = reverse('spese:balance')
        self.assertEqual(url, '/spese/balance/')
        url = reverse('spese:change', args=[19])
        self.assertEqual(url, '/spese/change/19/')
        url = reverse('spese:toggle', args=[19])
        self.assertEqual(url, '/spese/toggle/19/')
        url = reverse('spese:delete', args=[19])
        self.assertEqual(url, '/spese/delete/19/')
        
    def test_view_names(self):
        resolver = resolve('/spese/')
        # pdb.set_trace()
        self.assertEqual(resolver.func.__name__, 'index')
        resolver = resolve('/spese/19/')
        self.assertEqual(resolver.func.__name__, 'detail')
        resolver = resolve('/spese/add/')
        self.assertEqual(resolver.func.__name__, 'add')
        resolver = resolve('/spese/transfer_funds/')
        self.assertEqual(resolver.func.__name__, 'transfer_funds')
        resolver = resolve('/spese/balance/')
        self.assertEqual(resolver.func.__name__, 'balance')
        resolver = resolve('/spese/change/19/')
        self.assertEqual(resolver.func.__name__, 'change')
        resolver = resolve('/spese/toggle/19/')
        self.assertEqual(resolver.func.__name__, 'toggle')
        resolver = resolve('/spese/delete/19/')
        self.assertEqual(resolver.func.__name__, 'delete')
        

class SpeseViewsTestCase(TestCase):
    def setUp(self):
        # creating the user john
        self.client = Client()
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        # creating one expense for user john
        self.e = Expense(user=self.user, amount=-10)
        self.e.save()

    def test_index(self):
        # index for user john has one expense
        self.client.login(username='john', password='johnpassword')
        resp = self.client.get(reverse('spese:index', current_app='spese'))
        # pdb.set_trace()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('expenses_list' in resp.context)
        self.assertEqual([expense.pk for expense in resp.context['expenses_list']], [1])
        
class SpeseModelsTestCase(TestCase):
    def setUp(self):
        # creating the user john
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        # creating one account for user john
        self.a = Account(name='bank')
        self.a.save()
        self.a.users.add(self.user)
        self.a.save()

    def test_expense(self):
        # creating one expense for user john
        self.e = Expense(user=self.user, account=self.a, amount=-10)
        self.e.save()
        self.assertEqual(self.e.id, 1)

    def test_transferFund_easy(self):
        ### prepare
        # make a 2nd account (ac)
        self.ac = Account(name='cache')
        self.ac.save()
        self.ac.users.add(self.user)
        self.ac.save()
        # make 2 expenses
        self.e = Expense(user=self.user, account=self.a, amount=-10)
        self.e.save()
        self.e2 = Expense(user=self.user, account=self.ac, amount=+10)
        self.e2.save()
        ### make transferFund
        self.tf = TransferFund()
        self.tf.source = self.e
        self.tf.destination = self.e2
        self.tf.save()
        ### test
        self.assertEqual(self.tf.source.id,      self.e.id)
        self.assertEqual(self.tf.destination.id, self.e2.id)
        
    def test_transferFund_difficult(self):
        ### prepare
        # make a 2nd account (ac)
        self.ac = Account(name='cache')
        self.ac.save()
        self.ac.users.add(self.user)
        self.ac.save()
        # make 1 expense
        self.e = Expense(user=self.user, account=self.a, amount=-10)
        self.e.save()
        ### make: call TransferFund contructor and set by expense
        self.tf = TransferFund()
        self.tf.set(self.e, self.ac)
        ### test
        self.assertEqual(self.tf.source.id,      self.e.id)
        self.assertEqual(self.tf.destination.id, self.e.id+1)
        
    def test_get_companion(self):
        ### prepare
        # make a 2nd account (ac)
        ac = Account(name='cache')
        ac.save()
        ac.users.add(self.user)
        ac.save()
        # make 1 expense
        e = Expense(user=self.user, account=self.a, amount=-10)
        e.save()
        # and call TransferFund contructor with expense
        tf = TransferFund()
        tf.set(e, ac)
        ### make: companion expense
        companion = e.get_companion()
        ### test 
        self.assertEqual(tf.destination.id, companion.id)
        
    def test_get_companion_id(self):
        ### prepare
        # make a 2nd account (ac)
        ac = Account(name='cache')
        ac.save()
        ac.users.add(self.user)
        ac.save()
        # make 1 expense
        e = Expense(user=self.user, account=self.a, amount=-10)
        e.save()
        # and call TransferFund contructor with expense
        tf = TransferFund()
        tf.set(e, ac)
        ### make: companion expense
        c_id = e.get_companion_id()
        ### test 
        self.assertEqual(tf.destination.id, c_id)
        
    def test_has_companion(self):
        ### prepare
        # make a 2nd account (ac)
        ac = Account(name='cache')
        ac.save()
        ac.users.add(self.user)
        ac.save()
        # make 1 expense
        e = Expense(user=self.user, account=self.a, amount=-10)
        e.save()
        # call TransferFund contructor with expense
        tf = TransferFund()
        tf.set(e, ac)
        ### make
        tft = e.has_companion()
        ### test 
        self.assertTrue(tft)
        
    def test_delete_companion(self):
        ### prepare
        # make a 2nd account (ac)
        ac = Account(name='cache')
        ac.save()
        ac.users.add(self.user)
        ac.save()
        # make 1 expense
        e = Expense(user=self.user, account=self.a, amount=-10)
        e.save()
        e_id = e.id
        # call TransferFund contructor with expense
        tf = TransferFund()
        tf.set(e, ac)
        c = e.get_companion()
        c_id = c.id
        ### make
        e.delete_companion()       # delete c and tf
        ### test 
        cq = Expense.objects.filter(pk=c_id)
        tfq = TransferFund.objects.filter(Q(source_id=e_id)|Q(destination_id=c_id))
        # self.assertFalse(eq)
        self.assertFalse(cq)
        self.assertFalse(tfq)
        
    def test_delete_with_companion(self):
        ### prepare
        # make a 2nd account (ac)
        ac = Account(name='cache')
        ac.save()
        ac.users.add(self.user)
        ac.save()
        # make 1 expense
        e = Expense(user=self.user, account=self.a, amount=-10)
        e.save()
        e_id = e.id
        # call TransferFund contructor with expense
        tf = TransferFund()
        tf.set(e, ac)
        c = e.get_companion()
        c_id = c.id
        ### make
        e.delete_with_companion()        # delete e, c, tf
        ### test 
        eq = Expense.objects.filter(pk=e_id)
        cq = Expense.objects.filter(pk=c_id)
        tfq = TransferFund.objects.filter(Q(source_id=e_id)|Q(destination_id=c_id))
        # self.assertFalse(eq)
        self.assertFalse(cq)
        self.assertFalse(tfq)        