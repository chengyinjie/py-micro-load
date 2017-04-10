import logging
import uuid
import md5

logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(pathname)s: %(lineno)s] %(message)s', level=logging.INFO)
logger = logging.getLogger('testing')

def hl(s):
    '''
    red background
    '''
    return '\033[41m%s\033[0m' % s

def hl2(s):
    '''
    yellow background, black frontground
    '''
    return '\033[43;30m%s\033[0m' % s
    
def get_random_name():
    rname = str(uuid.uuid4()).split('-')[0]
    pre = 'autotest-'
    return pre + rname

def get_random_authcode():
    name = get_random_name()
    m = md5.new(name).hexdigest()
    return m

