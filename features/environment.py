# -*- coding: UTF-8 -*-
"""
before_step(context, step), after_step(context, step)
    These run before and after every step.
    The step passed in is an instance of Step.

before_scenario(context, scenario), after_scenario(context, scenario)
    These run before and after each scenario is run.
    The scenario passed in is an instance of Scenario.

before_feature(context, feature), after_feature(context, feature)
    These run before and after each feature file is exercised.
    The feature passed in is an instance of Feature.

before_tag(context, tag), after_tag(context, tag)

"""

# -- SETUP: Use cfparse as default matcher
# from behave import use_step_matcher
# step_matcher("cfparse")

from steps import account_model
import logging, boto3

def before_all(context):
    logging.basicConfig(filename="behave.log")
#    context.config.setup_logging(filename="behave.log")
#    if not context.config.log_capture:
#    logging.basicConfig(level=logging.DEBUG)
#    behave.log_capture.capture(context,)
    context.scpids=[]
    context.scpnames=['ScpBlockCloudTrailCfgAccess','ScpApprovedProductionSvcs','ScpDeniedApplicationSvcs']
    try:
        org=boto3.client('organizations')
        response=org.create_policy(
        	Content='{\
    "Version": "2012-10-17",\
    "Statement": [\
        {\
            "Sid": "Stmt1234567890123",\
            "Effect": "Deny",\
            "Action": [       \
                "cloudtrail:AddTags",     \
                "cloudtrail:CreateTrail", \
                "cloudtrail:DeleteTrail", \
                "cloudtrail:RemoveTags",  \
                "cloudtrail:StartLogging",\
                "cloudtrail:StopLogging", \
                "cloudtrail:UpdateTrail"  \
            ],\
            "Resource": [\
                "*"\
            ]\
        }\
    ]\
}',
			Description='Prevents anyone in any of the member accounts from creating or modifying any AWS CloudTrail logs that we configure.',
			Name=context.scpnames[0],
			Type='SERVICE_CONTROL_POLICY'
        )
        logging.info(response)
        context.scpids.append(response['Policy']['Id'])
    except Exception as e:
        logging.warn(e)

    try:
        response=org.create_policy(
        	Content='{\
    "Version": "2012-10-17",\
    "Statement": [\
        {\
            "Sid": "Stmt1111111111111",\
            "Effect": "Allow",\
            "Action": [ \
                "ec2:*",\
                "elasticloadbalancing:*",\
                "codecommit:*",\
                "cloudtrail:*",\
                "codedeploy:*"\
              ],\
            "Resource": [ "*" ]\
        }\
    ]\
}',
        	Description='an allow list of all the services and actions that you want to enable for users and roles in the Production OU.',
			Name=context.scpnames[1],
        	Type='SERVICE_CONTROL_POLICY'
        )
        logging.info(response)
        context.scpids.append(response['Policy']['Id'])
    except Exception as e:
        logging.warn(e)

    try:
        response=org.create_policy(
        	Content='{\
  "Version": "2012-10-17",\
  "Statement": [\
    {\
      "Effect": "Deny",\
      "Action": [ "dynamodb:*" ],\
      "Resource": [ "*" ]\
    }\
  ]\
}',
        	Description='A deny list of services that are blocked from use in the MainApp OU.',
			Name=context.scpnames[2],
        	Type='SERVICE_CONTROL_POLICY'
        )
        logging.info(response)
        context.scpids.append(response['Policy']['Id'])
    except Exception as e:
        logging.warn(e)

# def after_scenario(context,scenario):
#     model = getattr(context, "model", None)
#     if model:
#     	for user_model in context.model.user_models:
#     		user_model.clean_user()

def detach_all(context):
	sess = boto3.session.Session(
		profile_name='default')
	org=sess.client('organizations')
	response=org.list_policies_for_target(
    	TargetId=context.model.accountid,
    	Filter='SERVICE_CONTROL_POLICY'
	)
	for policy in response['Policies']:
		if policy["Name"] in context.scpnames:
			logging.info('Detaching'+policy['Name']
				+' from '+accountid)
			org.client.detach_policy(
				PolicyId=policy['Id'],
				TargetId=context.model.accountid
			)

def after_all(context):
	#print(buffer)
	#print(context.buffer)
	# try:
	# 	org=boto3.client('organizations')
	# 	response=org.delete_policy(
	# 		PolicyId=context.scpids[0]
	# 	)
	# except Exception as e:
	# 	logging.warn(e)
	# try:
	# 	response=org.delete_policy(
	# 		PolicyId=context.scpids[1]
	# 	)
	# except Exception as e:
	# 	logging.warn(e)
	# try:
	# 	response=org.delete_policy(
	# 		PolicyId=context.scpids[2]
	# 	)
	# except Exception as e:
	# 	logging.warn(e)
	try:
		detach_all(context)
	except Exception as e:
		logging.warn(e)

