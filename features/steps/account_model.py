# -*- coding: UTF-8 -*-
"""
Based on ``behave tutorial``

Feature: Step Setup Table

   Scenario: Setup Table
     Given a set of specific users
        | name      | department  |
        | Barry     | Beer Cans   |
        | Pudey     | Silly Walks |
        | Two-Lumps | Silly Walks |

    When we count the number of people in each department
    Then we will find two people in "Silly Walks"
     But we will find one person in "Beer Cans"
"""

# @mark.domain_model
# -----------------------------------------------------------------------------
# DOMAIN-MODEL:
# -----------------------------------------------------------------------------
import json, boto3, botocore, logging
from user_model import *


class AccountModel(object):
    def __init__(self,accountid,profilename='default'):
        # Assert the account exists
        try:
            sess = boto3.session.Session(
                profile_name='default'
            )
            logging.info("default.Session="+str(dir(sess)))
            self.super_access_key=sess.get_credentials().access_key
            self.super_secret_key=sess.get_credentials().secret_key
            logging.info("SuperCredentials("
                +profilename+","
                +self.super_access_key+","
                +self.super_secret_key+")"
            )           
            sess.client('organizations').describe_account(
                AccountId=accountid
            )
        except Exception as e:
            logging.error(e)
            raise e

        sess = boto3.session.Session(
            profile_name=profilename
        )
        self.access_key=sess.get_credentials().access_key
        self.secret_key=sess.get_credentials().secret_key
        logging.info("AccountCredentials("
                +profilename+","
                +self.access_key+","
                +self.secret_key+")"
        )
        self.accountid=accountid
        self.users=[]
        self.user_models=[]


    def get_iam(self):
        sess = boto3.session.Session(
            aws_access_key_id=self.access_key, 
            aws_secret_access_key=self.secret_key
        )
        return sess.client('iam')

    def get_org(self):
        sess = boto3.session.Session(
            aws_access_key_id=self.super_access_key, 
            aws_secret_access_key=self.super_secret_key
        )
        return sess.client('organizations')

    def add_user(self,username,groupname):
        assert username not in self.users

        user_model=UserModel(username,groupname)
        user_model.configure(username,groupname,self.get_iam())
        self.users.append(username)
        self.user_models.append(user_model)
        return user_model

    def del_user(self,username):
        assert username in self.users
        self.get_iam().delete_user(
            UserName=username
        )
        self.users.remove(username)

    def show_user(self,username):
        logging.debug("AccountModel.show_user()")
        assert username in self.users
        response=self.get_iam().get_user(
            UserName=username
        )
        loggging.debug(response)
        return response

    def get_policyid(self,policyname):
        policyid=None
        try:
            response=self.get_org().list_policies(
                Filter='SERVICE_CONTROL_POLICY'
            )
            policylist=response['Policies']
            for policy in policylist:
                if policy['Name']==policyname:
                    policyid=policy['Id']
                    break
        except Exception as e:
            raise e
        return policyid

    def attach_policy(self,policyid):
        assert policyid
        try:
            self.get_org().attach_policy(
                PolicyId=policyid,
                TargetId=self.accountid
            )
        except Exception as e:
            raise e

    def detach_policy(self,policyid):
        assert policyid
        try:
            self.get_org().detach_policy(
                PolicyId=policyid,
                TargetId=self.accountid
            )
        except Exception as e:
            raise e

    def detach_all(self,context):
        org=self.get_org()
        response=org.list_policies_for_target(
            TargetId=context.model.accountid,
            Filter='SERVICE_CONTROL_POLICY'
        )
        for policy in response['Policies']:
            logging.info('Considering policyname '+ policy['Name'])
            if policy["Name"] in context.scpnames:
                logging.info('Detaching'+policy['Name']
                    +' from '+context.model.accountid)
                org.detach_policy(
                    PolicyId=policy['Id'],
                    TargetId=context.model.accountid
                )


