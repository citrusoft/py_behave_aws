# -*- coding: UTF-8 -*-
"""
Based on ``behave tutorial`` and ``aws tutorial``

   Scenario: Deny list for PGEApp prohibited services.
     Given pge-application users of account, PGEAppAccount, with id, 123133550781
        | name   | groupname     |
        | Sunil  | Administrator |
        | Tushir | Administrator |
     When attempts are made to invoke services:
         | resource | method             | params  |
         | dynamodb | list_global_tables |         |
         | dynamodb | delete_table       | popcorn |
     Then the service responds with code 403
"""

# @mark.steps
# ----------------------------------------------------------------------------
# STEPS:
# ----------------------------------------------------------------------------
import logging
from behave   import given, when, then
from hamcrest import assert_that, equal_to
from testutil import NamedNumber
from account_model import AccountModel, UserModel

@given('nada state')
def step_impl(context):
    pass

@when('nada event')
def step_impl(context):
    pass

@then('nada result')
def step_impl(context):
    pass
