Feature: PGE Application Service Control Policies (TestScpDeniedApplicationSvcs)

   Scenario: Services available to PGEApp.
     Given pge-application users of account, root, with id, 919568423267
         | name   | groupname      |
         | Tommy  | Administrators |
     When attempts are made to invoke services:
         | resource | method             | params |
         | dynamodb | list_global_tables | none   |
         | dynamodb | describe_limits    | none   |
     Then each service call responds with code 200

   Scenario: Administrators override Deny list for PGEApp prohibited services.
     Given pge-application users of account, root, with id, 919568423267
         | name   | groupname      |
         | Tommy  | Administrators |
     When Service Control Policy, ScpDeniedApplicationSvcs, is attached:
     Then each service call responds as described below:
         | resource | method             | params | code |
         | dynamodb | list_global_tables | none   | 200  |
         | dynamodb | describe_limits    | none   | 200  |

   Scenario: Deny list for PGEApp prohibited services.
     Given pge-application users of account id, 123133550781, with profile, thunt
         | name   | groupname      |
         | Steve  | PGEAppUsers    |
     When Service Control Policy, ScpDeniedApplicationSvcs, is attached:
     Then each service call responds as described below:
         | resource | method             | params | code |
         | dynamodb | list_global_tables | none   | 403  |
         | dynamodb | describe_limits    | none   | 403  |

