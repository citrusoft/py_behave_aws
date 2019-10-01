import json, boto3, botocore, logging


class UserModel(object):
    def __init__(self,username,groupname):
        logging.info("CONSTRUCTING UserModel "+username)
        self.http_status_codes=[]
        self.resources=[]
        self.methods=[]
        self.params=[]
        self.username=username
        self.access_key=''
        self.secret_key=''

    def user_exists(self,username,iam):
        exists=False
        try:
            iam.get_user(
                UserName=username
            )
            exists=True
        except Exception as e:
            logging.warning(e)
        return exists

    def configure(self,username,groupname,iam):
        logging.info("UserModel.configure("+username+","+groupname+")")
        if self.user_exists(username,iam):
        	if username=='Tommy':
        		self.access_key='AKIA5MGUMTFR35IZ3BVM'
        		self.secret_key='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'
        	if username=='Steve':
        		self.access_key='AKIARZK2U4C6TZLKGVF5'
        		self.secret_key='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'
            #self.clean_user(iam)
        else:
        	logging.info('CREATING USER '+username)
        	response = iam.create_user(
        	    UserName=username
        	)
        	logging.info("CREATED! "+response.__str__())
        	iam.add_user_to_group(
        	    GroupName=groupname,
        	    UserName=username
        	)
        	access_key=iam.create_access_key(
        	    UserName=username       
        	)
        	self.access_key=access_key["AccessKey"]["AccessKeyId"]
        	self.secret_key=access_key["AccessKey"]["SecretAccessKey"]
        logging.info("UserCredentials("
                +username+","
                +self.access_key+","
                +self.secret_key+")"
	    )

    def clean_user(self,iam):
            logging.info('DELETING USER '+self.username)
            username=self.username
            # PRECONDITION: remove user from groups
            groups=iam.list_groups_for_user(
                UserName=username
            )
            logging.debug(groups)
            for group in groups["Groups"]:
                iam.remove_user_from_group(
                    GroupName=group["GroupName"],
                    UserName=username
                )
            # PRECONDITOON: remove access keys
            accesskeys=iam.list_access_keys(
                UserName=username
            )
            for key in accesskeys["AccessKeyMetadata"]:
                iam.delete_access_key(
                    UserName=username,
                    AccessKeyId=key["AccessKeyId"]
                )
            iam.delete_user(
                UserName=username
            )

    def show_user(self,username,iam):
        logging.info("UserModel.show_user("+username+")")
        try:
            response=iam.get_user(
                UserName=username
            )
            logging.debug(response)
        except Exception as e:
            logging.warning(e)
            response=""
        return response

    def invoke(self,resource,method,params=''):
        logging.info("UserModel.invoke("+resource+","+method+","+params+")")
        http_status_code=-1
        self.resources.append(resource)
        self.methods.append(method)
        self.params.append(params)
        try:
            logging.info("AWS.boto3.client("
                +resource+","
                +self.access_key+","
                +self.secret_key+")"
            )
            sess = boto3.session.Session(
                aws_access_key_id=self.access_key, 
                aws_secret_access_key=self.secret_key,
                aws_session_token=''
            )
            client = sess.client(resource)
            if params.lower() == 'none':
                params=''
            # response=client.list_global_tables()
            expression='client.'+method+'('+params+')'
            logging.info('INVOKE: '+expression)
            response=eval(expression)
            logging.info(response)
            http_status_code=int(response["ResponseMetadata"]["HTTPStatusCode"])
        except botocore.exceptions.ClientError as e:
            logging.warning(e)
            http_status_code=403
            # if 'ResponseMetaData' in e.response:
            #     logging.warning(e.response)
            #     http_status_code=int(e.response["ResponseMetadata"]["HTTPStatusCode"])
        except Exception as e:
            logging.warning(e)

        self.http_status_codes.append(int(http_status_code))
        return int(http_status_code)
