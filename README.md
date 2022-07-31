### Instructions for running the tests:
* `cd deployment/`
* `docker-compose up -d --build`
* `docker exec -it git_tests pytest`
* `docker-compose stop`


### Main restrictions:
- tests are covering one most popular scenario in GIT workflow:
  - git clone <repo>
  - git checkout -b <branch>
  - git add <file>
  - git commit -m <message>
  - git push origin <branch>
- tests are covering basic command behaviour, with no negative cases
- in order to be as much close to real GIT usage as possible, no additional Git libraries (SDK) are used. 
  Git Commands are executed with Subprocess(local), Pexpect(local with interactive input) or Paramiko(ssh) libraries.
- there are two environments (containers):
  - test server - all tests are running in this environment
  - git server - remote git instance, with ssh server enabled
- both environment are configured by Ansible Playbooks before tests start (session scope fixture)
- tests are executed in Pytest framework, with extensions: pytest-dependency and pytest-order
- grappa library is used for assertions (and much better error output for Pytest)


### What to do next:
1. Environment and code structure:
   - introduction of public/private keys for authentication
   - Specific, unambiguous and the same GIT versions on all containers! GIT is extremely backward compatible,
     but major rule of testing: we need to exactly know which version we are testing!
     (not implemented due to time-consuming issues with mirrors)
   - Ansible playbooks evolution and adaptation; currently they are doing basic configuration
   - wrapper to compose - tests container should not/can not be active all the time
   - better documentation - especially for ansible-related files
   - automatic or semi-automatic static code analysis - mypy, black, pylint

2. Tests phase v2:
    - more specific tests for already tested commands, including negative cases
    - design and implementation of more workflow scenarios
    - In order to run tests in a CI loop, they need to be faster, so parallel execution can be introduced.
      Additionally, environment configuration can be moved outside Pytest, for better control over it.
      And last but not least, proper logging and test results artifacts generation must be introduced, in order to track errors with better accuracy.
3. Tests - later phases:
   - after all major workflow scenarios will be covered, another test types can be implemented
   - for the CI loop, centralized test manager / data collector (e.g. API, or ETL pipelines) can be introduced, in order to get better knowledge about environment and tests.