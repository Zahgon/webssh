import logging
import os.path
import threading
import paramiko


def load_host_keys(path):
    if os.path.exists(path) and os.path.isfile(path):
        return paramiko.hostkeys.HostKeys(filename=path)
    return paramiko.hostkeys.HostKeys()


def get_policy_dictionary():
    dic = {
       k.lower(): v for k, v in vars(paramiko.client).items() if type(v)
       is type and issubclass(v, paramiko.client.MissingHostKeyPolicy)
       and v is not paramiko.client.MissingHostKeyPolicy
    }
    return dic


def get_policy_class(policy):
    origin_policy = policy
    policy = policy.lower()
    if not policy.endswith('policy'):
        policy += 'policy'

    dic = get_policy_dictionary()
    logging.debug(dic)

    try:
        cls = dic[policy]
    except KeyError:
        raise ValueError('Unknown policy {!r}'.format(origin_policy))
    return cls


def check_policy_setting(policy_class, host_keys_settings):
    host_keys = host_keys_settings['host_keys']
    host_keys_filename = host_keys_settings['host_keys_filename']
    system_host_keys = host_keys_settings['system_host_keys']

    if policy_class is paramiko.client.AutoAddPolicy:
        host_keys.save(host_keys_filename)  # for permission test
    elif policy_class is paramiko.client.RejectPolicy:
        if not host_keys and not system_host_keys:
            raise ValueError(
                'Reject policy could not be used without host keys.'
            )


class AutoAddPolicy(paramiko.client.MissingHostKeyPolicy):
    """
    thread-safe AutoAddPolicy
    """
    lock = threading.Lock()




paramiko.client.AutoAddPolicy = AutoAddPolicy
