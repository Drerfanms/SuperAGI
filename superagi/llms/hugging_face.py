import os
import requests
import json
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.llms.utils.huggingface_utils.tasks import Tasks, TaskParameters
from superagi.llms.utils.huggingface_utils.public_endpoints import ACCOUNT_VERIFICATION_URL

class HuggingFace(BaseLlm):
	def __init__(
		self,
		api_key,
		model,
		end_point,
		task=Tasks.TEXT_GENERATION,
		**kwargs
	):
		self.api_key = api_key
		self.model = model
		self.end_point = end_point
		self.task = task
		self.task_params = TaskParameters().get_params(self.task, **kwargs)
		self.headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
		}

	def get_source(self):
			return "hugging face"

	def get_api_key(self):
		"""
		Returns:
			str: The API key.
		"""
		return self.api_key

	def get_model(self):
		"""
		The API needs a POST request with the parameter "inputs".

		Returns:
			response from the endpoint
		"""
		# Returning the endpoint response from the function `get_model` is not a good idea. If the model name is not accessible, it is better to return a fixed schema for now that informs the user about the situation and a possible fix.
# 		data = json.dumps({"inputs": "validating end_point"})
# 		response = requests.post(self.end_point, headers=self.headers, data=data)
# 		model = response.json()

		return self.model

	def get_models(self):
		"""
		Returns:
			str: The model.
		"""
		return self.model

	def verify_access_key(self):
		"""
		Verify the access key is valid.

		Returns:
			bool: True if the access key is valid, False otherwise.
		"""
		response = requests.get(ACCOUNT_VERIFICATION_URL, headers=self.headers)

		# A more sophisticated check could be done here. 
		# Ideally we should be checking the response from the endpoint along with the status code. 
		# If the desired response is not received, we should return False and log the response.
		return response.status_code == 200

	def chat_completion(self, messages, max_tokens=100):
		"""
		Call the HuggingFace inference API.
		Args:
			messages (list): The messages.
			max_tokens (int): The maximum number of tokens.
		Returns:
			dict: The response.
		"""
		try:
			params = self.task_params
			if self.task == Tasks.TEXT_GENERATION:
				params["max_new_tokens"] = max_tokens
			payload = {
				"inputs": messages,
				"parameters": self.task_params,
				"options": {
					"use_cache": False,
					"wait_for_model": True,
				}
			}
			response = requests.post(self.end_point, headers=self.headers, data=json.dumps(payload))
			completion = json.loads(response.content.decode("utf-8"))
			if self.task == Tasks.TEXT_GENERATION:
				content = completion[0]["generated_text"]
			else:
				content = completion[0]["answer"]

			return {"response": completion, "content": content}
		except Exception as exception:
			# logger.info("HF Exception:", exception)
			return {"error": "ERROR_HUGGINGFACE", "message": "HuggingFace Inference exception"}