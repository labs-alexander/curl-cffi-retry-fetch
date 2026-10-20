import config
import exceptions as exc

import time
import random
import logging
from curl_cffi.requests import Session


logger = logging.getLogger(__name__)


def apply_retry(function, max_tries=10):
	def retry(*args, **kwargs):
		for attempt in range(max_tries + 1):

			delay = 10 * attempt + random.uniform(0, 3)

			try:
				return function(*args, **kwargs)

			except exc.RetryableError as err:
				last_err = err
				logger.warning("Retryable error: %s", err)

			except exc.BlockedError as err:
				last_err = err
				logger.warning("Blocked: %s", err)
				#handle_blocked(session) //  your block handling logic here	

			except exc.UnknownError as err:
				last_err = err
				logger.warning("Unknown error: %s", err)
				raise

			except exc.FatalError as err:
				logger.error("Fatal error: %s", err)
				raise

			if attempt < max_tries:
				time.sleep(delay)

		raise last_err

	return retry


@apply_retry
def fetch(url, session=None, params=None, headers=None):
	if session is None:
		session = create_session()
	response = session.get(url=url, headers=headers, params=params)
	classify_response(response)
	return response


def classify_response(response):
	if response.ok:
		return response

	exception_class = exc.STATUS_MAP.get(response.status_code, exc.UnknownError)	
	raise exception_class(response)


def create_session(proxy=None, impersonate="chrome"):
	proxies = {"http": proxy, "https": proxy} if proxy else None
	session = Session(impersonate=impersonate, proxy=proxies)
	session.proxy_url = proxy
	return session


def handle_blocked():
	pass
