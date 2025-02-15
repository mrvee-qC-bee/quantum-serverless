import json
import os.path

from django.contrib.auth.models import User
from django.core.files import File
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Program


class ProgramTests(APITestCase):
    fixtures = ["tests/fixtures/initial_data.json"]

    def test_get_program_returns_200(self):
        """
        Retrieve information about a specific program
        """
        program_id = "1a7947f9-6ae8-4e3d-ac1e-e7d608deec82"
        url = reverse("v1:programs-detail", args=[program_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_created_program_returns_404(self):
        """
        Retrieve information about a specific program that doesn't exist returns a 404
        """
        url = reverse("v1:programs-detail", args=[2])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_program_unauthenticated_returns_403(self):
        """
        Create a program without being authenticated returns a 403
        """
        program_input = {}

        url = reverse("v1:programs-list")
        response = self.client.post(url, data=program_input, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_program_with_empty_object_validation(self):
        """
        Create a program with an empty object as input should return a validation error
        """
        program_input = {}
        fields_to_check = ["title", "entrypoint", "artifact"]
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")
        response = self.client.post(url, data=program_input, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        failed_validation_fields_list = list(response.json().keys())
        self.assertListEqual(failed_validation_fields_list, fields_to_check)

    def test_create_program_with_blank_values_validation(self):
        """
        Create a program with an object with blank values should return a validation error
        """
        program_input = {
            "title": "",
            "description": "",
            "entrypoint": "",
            "working_dir": "",
            "version": "",
            "dependencies": None,
            "env_vars": None,
            "arguments": None,
            "tags": None,
            "public": True,
        }
        fields_to_check = ["title", "entrypoint", "working_dir", "version", "artifact"]
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")
        response = self.client.post(url, data=program_input, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        failed_validation_fields_list = list(response.json().keys())
        self.assertListEqual(failed_validation_fields_list, fields_to_check)

    def test_create_program_returns_201(self):
        """
        Create a program
        """
        program_input = {
            "title": "Awesome program",
            "description": "Awesome program description",
            "entrypoint": "program.py",
            "working_dir": "./",
            "version": "0.0.1",
            "env_vars": json.dumps({"DEBUG": True}),
            "arguments": json.dumps({}),
            "tags": json.dumps(["dev"]),
            "dependencies": json.dumps([]),
            "public": True,
        }
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")
        with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "fixtures",
                "artifact.tar",
            ),
            "rb",
        ) as file:
            program_input["artifact"] = file
            response = self.client.post(url, data=program_input, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 2)

    def test_count_of_all_programs_created_must_be_one(self):
        """
        List all the programs created and check that there is one
        """
        url = reverse("v1:programs-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_delete_program_unauthenticated_returns_403(self):
        """
        Delete a program with an unauthenticated user
        """
        program_id = "1a7947f9-6ae8-4e3d-ac1e-e7d608deec82"

        url = reverse("v1:programs-detail", args=[program_id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_a_non_created_program_returns_404(self):
        """
        Delete a program that doesn't exist returns a 404
        """
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-detail", args=[2])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_program_returns_204(self):
        """
        Delete a program that exists 204
        """
        program_id = "1a7947f9-6ae8-4e3d-ac1e-e7d608deec82"
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-detail", args=[program_id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Program.objects.count(), 0)

    def test_program_list_validation_returns_400(self):
        """
        The value for dependencies and tags is a dict, a non-allowed value for these fields and returns a 400
        """
        fields_to_check = ["dependencies", "tags"]
        program_input = {
            "title": "Awesome program",
            "description": "Awesome program description",
            "entrypoint": "program.py",
            "working_dir": "./",
            "version": "0.0.1",
            "dependencies": json.dumps({}),
            "env_vars": json.dumps({"DEBUG": True}),
            "arguments": json.dumps(None),
            "tags": json.dumps({}),
            "public": True,
        }
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")
        with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "fixtures",
                "artifact.tar",
            ),
            "rb",
        ) as file:
            program_input["artifact"] = file
            response = self.client.post(url, data=program_input, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        failed_validation_fields_list = list(response.json().keys())
        self.assertListEqual(failed_validation_fields_list, fields_to_check)

    def test_program_dict_validation_returns_400(self):
        """
        The value for env_vars and arguments is a list, a non-allowed value for these fields and returns a 400
        """
        fields_to_check = ["env_vars", "arguments"]
        program_input = {
            "title": "Awesome program",
            "description": "Awesome program description",
            "entrypoint": "program.py",
            "working_dir": "./",
            "version": "0.0.1",
            "dependencies": json.dumps([]),
            "env_vars": json.dumps([]),
            "arguments": json.dumps([]),
            "tags": json.dumps(["dev"]),
            "public": True,
        }
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")
        with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "fixtures",
                "artifact.tar",
            ),
            "rb",
        ) as file:
            program_input["artifact"] = file
            response = self.client.post(url, data=program_input, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        failed_validation_fields_list = list(response.json().keys())
        self.assertListEqual(failed_validation_fields_list, fields_to_check)

    def test_program_artifact_validation_returns_400(self):
        """
        The value for artifact is not a tar file, a non-allowed value for this field and returns a 400
        """
        fields_to_check = ["artifact"]
        program_input = {
            "title": "Awesome program",
            "description": "Awesome program description",
            "entrypoint": "program.py",
            "working_dir": "./",
            "version": "0.0.1",
            "env_vars": json.dumps({"DEBUG": True}),
            "arguments": json.dumps({}),
            "tags": json.dumps(["dev"]),
            "dependencies": json.dumps([]),
            "public": True,
        }
        test_user = User.objects.get(username="test_user")

        self.client.force_login(test_user)

        url = reverse("v1:programs-list")

        with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "fixtures",
                "initial_data.json",
            )
        ) as file:
            program_input["artifact"] = File(file)
            response = self.client.post(url, data=program_input, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        failed_validation_fields_list = list(response.json().keys())
        self.assertListEqual(failed_validation_fields_list, fields_to_check)
