import boto3, logging
from behave   import given, when, then
from hamcrest import *
from testutil import NamedNumber
from account_model import *

@given('pge-application users of account, {accountname}, with id, {accountid}')
def step_impl(context, accountname, accountid):
    model = getattr(context, "model", None)
    if not model:
        context.model = AccountModel(accountid)
    for row in context.table:
        context.model.add_user(username=row["name"], groupname=row["groupname"])

@when('attempts are made to invoke services')
def step_impl(context):
    model = getattr(context, "model", None)
    for usermodel in model.user_models:
        logging.debug(usermodel)
        for row in context.table:
            if row["params"].lower()!="none":
                usermodel.invoke(row["resource"],row["method"],row["params"])
            else:
                usermodel.invoke(row["resource"],row["method"])

@then('each service call responds with code {errorcode}')
def step_impl(context, errorcode):
    model = getattr(context, "model", None)
    for usermodel in model.user_models:
        print("USER="+usermodel.username)
        print("resource\tmethod\tparams\treturncode")
        for i in range(len(usermodel.http_status_codes)):
            print(usermodel.resources[i]+"\t"
                + usermodel.methods[i]+"\t"
                + usermodel.params[i]+"\t"
                + str(usermodel.http_status_codes[i]))
            assert usermodel.http_status_codes[i] == int(errorcode)

@given('pge-application users of account id, {accountid}, with profile, {profilename}')
def step_impl(context, accountid, profilename):
    model = getattr(context, "model", None)
    if not model:
        context.model = AccountModel(accountid,profilename)
    for row in context.table:
        context.model.add_user(username=row["name"], groupname=row["groupname"])

@when('Service Control Policy, {scp}, is attached:')
def step_impl(context, scp):
    model = getattr(context, "model", None)
    assert_that(model,not_none(), 'Account model required.')
    model.detach_all(context)
    id=model.get_policyid(scp)
    assert_that(id,not_none(), 
        'Cannot find Service Control Policy, '
        +scp
     )
    model.attach_policy(id)

@then('each service call responds as described below')
def step_impl(context):
    model = getattr(context, "model", None)
    for usermodel in model.user_models:
        logging.debug(usermodel)
        for row in context.table:
            assert_that(usermodel.invoke(row["resource"],row["method"],row["params"])
                ,equal_to(int(row['code']))
            )

