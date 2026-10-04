#!/usr/bin/env python3
"""Recorded semantic routes plus independent negative constraint checks."""
import copy
import unittest
from framework import ROOT, load, read_yaml, resolve, selection_errors, validate

class RouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load()

    def test_routing_cases(self):
        for case in read_yaml(ROOT/'tests/routing-cases.yaml')['cases']:
            with self.subTest(case=case['id']):
                route = resolve(case['decision'],self.config)
                self.assertEqual(route['tasks'],case['expected_tasks'])
                self.assertEqual(route['domains'],case['expected_domains'])
                self.assertTrue(set(case['expected_include']) <= set(route['skills']))
                self.assertFalse(set(case['expected_exclude']) & set(route['skills']))
                if 'expected_max_primary_skills' in case:
                    self.assertLessEqual(max(map(len,route['phases'].values()),default=0),case['expected_max_primary_skills'])

    def test_enabled_duplicate_owner_rejected(self):
        c=copy.deepcopy(self.config)
        c['skills']['skills']['anthropic-frontend-design']['enabled']=True
        errors=validate(config=c,check_revisions=False)
        self.assertTrue(any('duplicate enabled responsibility' in e for e in errors))
        self.assertTrue(any('enabled conflict' in e for e in errors))

    def test_disabled_owner_not_active(self):
        route=resolve({'tasks':['design'],'domains':['web'],'complexity':'small'},self.config)
        self.assertNotIn('anthropic-frontend-design',route['skills'])
        errors=selection_errors(['anthropic-frontend-design'],self.config['skills']['skills'],'small')
        self.assertTrue(any('disabled' in e for e in errors))

    def test_default_disabled_metadata_is_respected(self):
        c=copy.deepcopy(self.config)
        c['skills']['skills']['ui-ux-pro-max']['enabled_by_default']=False
        route=resolve({'tasks':['design'],'domains':['web'],'complexity':'small'},c)
        self.assertNotIn('ui-ux-pro-max',route['skills'])

    def test_conflict_even_when_optional_allowed(self):
        errors=selection_errors(['ui-ux-pro-max','anthropic-frontend-design'],self.config['skills']['skills'],'medium',True)
        self.assertTrue(any('conflict' in e for e in errors))
        self.assertTrue(any('duplicate responsibility' in e for e in errors))

    def test_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'budget exceeded'):
            resolve({'tasks':['feature'],'domains':[],'complexity':'trivial',
                     'conditions':{'ambiguous':True,'plan_needed':True}},self.config)

    def test_false_flags_do_not_load_optional_work(self):
        route=resolve({'tasks':['feature'],'domains':['react','web'],'complexity':'small'},self.config)
        self.assertEqual(route['skills'],['verification-before-completion'])

    def test_invalid_conditions_and_domains(self):
        for d in [{'tasks':['feature'],'domains':['made-up']},
                  {'tasks':['feature'],'conditions':{'browser_needed':'false'}},
                  {'tasks':['feature'],'conditions':{'unknown':True}}]:
            with self.subTest(decision=d), self.assertRaises(ValueError): resolve(d,self.config)

    def test_missing_source_resource_lock_and_conflict(self):
        for field,value,needle in [('source','missing/SKILL.md','missing skill entrypoint'),
                                   ('resources',['missing/resource'],'missing resource'),
                                   ('upstream','missing','missing upstream lock'),
                                   ('conflicts',['missing'],'unknown conflict'),
                                   ('domains',['missing'],'unknown domain'),
                                   ('task_types',['missing'],'unknown task/workflow')]:
            with self.subTest(field=field):
                c=copy.deepcopy(self.config)
                c['skills']['skills']['systematic-debugging'][field]=value
                self.assertTrue(any(needle in e for e in validate(config=c,check_revisions=False)))

    def test_path_escape_rejected(self):
        c=copy.deepcopy(self.config)
        c['skills']['skills']['research']['source']='../outside/SKILL.md'
        with self.assertRaisesRegex(ValueError,'escapes'): validate(config=c,check_revisions=False)

    def test_vendor_tampering_rejected(self):
        c=copy.deepcopy(self.config)
        up=c['upstream-lock']['upstreams']['security-guidance']
        up['files']['README.md']='0'*64
        self.assertTrue(any('integrity mismatch' in e for e in validate(config=c,check_revisions=False)))

    def test_unknown_workflow_rejected(self):
        c=copy.deepcopy(self.config)
        c['workflows']['task_workflows']['feature']='missing'
        self.assertTrue(any('unknown workflow' in e for e in validate(config=c,check_revisions=False)))

if __name__=='__main__': unittest.main(verbosity=2)
