
def get_config():
    import os
    import local_config as local_config
    import enclave_config as enclave_config
    ENV = os.environ.get("ENV")
    print("Environment:", ENV)
    if ENV == 'local':
        return local_config
    else:
        return enclave_config
    

