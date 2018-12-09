# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS-IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import types

from core.platform import models
from core.tests import test_utils
import feconf

(email_models,) = models.Registry.import_models([models.NAMES.email])


class SentEmailModelUnitTests(test_utils.GenericTestBase):

    """Test the SentEmailModel class."""


    def setUp(self):
        super(SentEmailModelUnitTests, self).setUp()

        # pylint: disable=unused-argument
        def _generate_hash_for_tests(
                cls, recipient_id, email_subject, email_body):
            return 'Email Hash'

        self.generate_constant_hash_ctx = self.swap(
            email_models.SentEmailModel, '_generate_hash',
            types.MethodType(
                _generate_hash_for_tests,
                email_models.SentEmailModel))

    def test_duplicate_mails_detected(self):
        email_models.SentEmailModel.create(
            'recipient_id', 'recipient@email.com', 'sender_id',
            'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
            'Email Subject', 'Email Body', datetime.datetime.utcnow())

        email_models.SentEmailModel.create(
            'recipient_id', 'recipient@email.com', 'sender_id',
            'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
            'Email Subject', 'Email Body', datetime.datetime.utcnow())

        duplicated = email_models.SentEmailModel.check_duplicate_message(
            'recipient_id', 'Email Subject', 'Email Body')

        self.assertEqual(duplicated, True)

        not_duplicated = email_models.SentEmailModel.check_duplicate_message(
            'recipient_id', 'Other Email Subject', 'Other Email Body')

        self.assertEqual(not_duplicated, False)



    def test_saved_model_can_be_retrieved_with_same_hash(self):
        with self.generate_constant_hash_ctx:
            email_models.SentEmailModel.create(
                'recipient_id', 'recipient@email.com', 'sender_id',
                'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
                'Email Subject', 'Email Body', datetime.datetime.utcnow())

            query = email_models.SentEmailModel.query()
            query = query.filter(
                email_models.SentEmailModel.email_hash == 'Email Hash')

            results = query.fetch(2)

            self.assertEqual(len(results), 1)

            query = email_models.SentEmailModel.query()
            query = query.filter(
                email_models.SentEmailModel.email_hash == 'Bad Email Hash')

            results = query.fetch(2)

            self.assertEqual(len(results), 0)

    def test_get_by_hash_works_correctly(self):
        with self.generate_constant_hash_ctx:
            email_models.SentEmailModel.create(
                'recipient_id', 'recipient@email.com', 'sender_id',
                'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
                'Email Subject', 'Email Body', datetime.datetime.utcnow())

            results = email_models.SentEmailModel.get_by_hash('Email Hash')

            self.assertEqual(len(results), 1)

            results = email_models.SentEmailModel.get_by_hash('Bad Email Hash')

            self.assertEqual(len(results), 0)

    def test_get_by_hash_returns_multiple_models_with_same_hash(self):
        with self.generate_constant_hash_ctx:
            email_models.SentEmailModel.create(
                'recipient_id', 'recipient@email.com', 'sender_id',
                'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
                'Email Subject', 'Email Body', datetime.datetime.utcnow())

            email_models.SentEmailModel.create(
                'recipient_id', 'recipient@email.com', 'sender_id',
                'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
                'Email Subject', 'Email Body', datetime.datetime.utcnow())

            results = email_models.SentEmailModel.get_by_hash('Email Hash')

            self.assertEqual(len(results), 2)

    def test_get_by_hash_behavior_with_sent_datetime_lower_bound(self):
        with self.generate_constant_hash_ctx:
            time_now = datetime.datetime.utcnow()

            email_models.SentEmailModel.create(
                'recipient_id', 'recipient@email.com', 'sender_id',
                'sender@email.com', feconf.EMAIL_INTENT_SIGNUP,
                'Email Subject', 'Email Body', datetime.datetime.utcnow())

            results = email_models.SentEmailModel.get_by_hash(
                'Email Hash', sent_datetime_lower_bound=time_now)
            self.assertEqual(len(results), 1)

            time_now1 = datetime.datetime.utcnow()

            results = email_models.SentEmailModel.get_by_hash(
                'Email Hash', sent_datetime_lower_bound=time_now1)
            self.assertEqual(len(results), 0)

            time_before = (datetime.datetime.utcnow() -
                           datetime.timedelta(minutes=10))

            results = email_models.SentEmailModel.get_by_hash(
                'Email Hash', sent_datetime_lower_bound=time_before)
            self.assertEqual(len(results), 1)

            # Check that it accepts only DateTime objects.
            with self.assertRaises(Exception):
                results = email_models.SentEmailModel.get_by_hash(
                    'Email Hash',
                    sent_datetime_lower_bound='Not a datetime object')



class ReplyToIdModelUnitTests(test_utils.GenericTestBase):


    """Test the GeneralFeedbackEmailReplyToIdModel class."""

    def setUp(self):
        super(ReplyToIdModelUnitTests, self).setUp()

        # pylint: disable=unused-argument
        def _generate_unique_id_for_tests(cls):
            return 'Non_unique_id'

        self.generate_constant_id_ctx = self.swap(
            email_models.GeneralFeedbackEmailReplyToIdModel,
            '_generate_unique_reply_to_id',
            types.MethodType(
                _generate_unique_id_for_tests,
                email_models.GeneralFeedbackEmailReplyToIdModel))

    def test_id_generation_works_correctly(self):
        # Name is too long for linter.
        model = email_models.GeneralFeedbackEmailReplyToIdModel

        created = model.create('user_id', 'thread_id')
        self.assertEqual(created.id, 'user_id.thread_id')

        created = model.create('other_user_id', 'other_thread_id')
        self.assertNotEqual(created.id, 'user_id.thread_id')

    def test_unique_reply_id_is_unique(self):
        # Name is too long for linter.
        model = email_models.GeneralFeedbackEmailReplyToIdModel

        all_ids = [
            model.create('user_id', 'thread_id').reply_to_id
            for _ in xrange(100)]
        set_ids = set(all_ids) #Set contains unique values
        self.assertEqual(len(all_ids), len(set_ids))

    def test_create_raises_when_duplicate_ids(self):
        with self.generate_constant_id_ctx, self.assertRaises(Exception):
            created1 = email_models.GeneralFeedbackEmailReplyToIdModel.create(
                'user_id', 'thread_id')
            created1.put()
            created2 = email_models.GeneralFeedbackEmailReplyToIdModel.create(
                'user_id', 'thread_id')
            created2.put()

    def test_get_by_reply_to_id_works_correctly(self):
        # Name is too long for linter.
        model = email_models.GeneralFeedbackEmailReplyToIdModel

        created = model.create('user_id', 'thread_id')
        created.put()

        result = model.get_by_reply_to_id(created.reply_to_id)

        self.assertNotEqual(result, None) #There should be a result
        self.assertEqual(result.reply_to_id, created.reply_to_id)

        result = model.get_by_reply_to_id('non_existent_reply_to_id')

        self.assertEqual(result, None)

    def test_get_works_correctly(self):
        created = email_models.GeneralFeedbackEmailReplyToIdModel.create(
            'user_id', 'thread_id')
        created.put()

        result = email_models.GeneralFeedbackEmailReplyToIdModel.get(
            'user_id', 'thread_id', strict=False)

        self.assertNotEqual(result, 1)

        result = email_models.GeneralFeedbackEmailReplyToIdModel.get(
            'bad_user_id', 'bad_thread_id', strict=False) #Should not throw
        self.assertEqual(result, None)

        with self.assertRaises(Exception):
            result = email_models.GeneralFeedbackEmailReplyToIdModel.get(
                'bad_user_id', 'bad_thread_id') #Should throw

    def test_get_multi_by_user_ids_works_correctly(self):
        # Name is too long for linter.
        model = email_models.GeneralFeedbackEmailReplyToIdModel

        model.create('user_id_1', 'thread_id')
        model.create('user_id_2', 'thread_id')

        result = model.get_multi_by_user_ids(
            ['user_id_1', 'user_id_2'], 'thread_id')

        self.assertEqual(len(result), 2)
        assert 'user_id_1' in result.keys()
        assert 'user_id_2' in result.keys()

    def test_user_id(self):
        result = email_models.GeneralFeedbackEmailReplyToIdModel.create(
            'user_id', 'entity_type.entity_id.thread_id')

        self.assertEqual(result.user_id, 'user_id')

    def test_entity_type(self):
        result = email_models.GeneralFeedbackEmailReplyToIdModel.create(
            'user_id', 'entity_type.entity_id.thread_id')

        self.assertEqual(result.entity_type, 'entity_type')

    def test_entity_id(self):
        result = email_models.GeneralFeedbackEmailReplyToIdModel.create(
            'user_id', 'entity_type.entity_id.thread_id')

        self.assertEqual(result.entity_id, 'entity_id')

    def test_thread_id(self):
        result = email_models.GeneralFeedbackEmailReplyToIdModel.create(
            'user_id', 'entity_type.entity_id.thread_id')

        self.assertEqual(result.thread_id, 'entity_type.entity_id.thread_id')


class GenerateHashTests(test_utils.GenericTestBase):

    """Test that generating hash functionality works as expected."""


    def test_same_inputs_always_gives_same_hashes(self):
        # pylint: disable=protected-access
        email_hash1 = email_models.SentEmailModel._generate_hash(
            'recipient_id', 'email_subject', 'email_html_body')

        email_hash2 = email_models.SentEmailModel._generate_hash(
            'recipient_id', 'email_subject', 'email_html_body')
        self.assertEqual(email_hash1, email_hash2)
        # pylint: enable=protected-access

    def test_different_inputs_give_different_hashes(self):
        # pylint: disable=protected-access
        email_hash1 = email_models.SentEmailModel._generate_hash(
            'recipient_id', 'email_subject', 'email_html_body')

        email_hash2 = email_models.SentEmailModel._generate_hash(
            'recipient_id', 'email_subject', 'email_html_body2')
        self.assertNotEqual(email_hash1, email_hash2)

        email_hash2 = email_models.SentEmailModel._generate_hash(
            'recipient_id2', 'email_subject', 'email_html_body')
        self.assertNotEqual(email_hash1, email_hash2)

        email_hash2 = email_models.SentEmailModel._generate_hash(
            'recipient_id', 'email_subject2', 'email_html_body')
        self.assertNotEqual(email_hash1, email_hash2)

        email_hash2 = email_models.SentEmailModel._generate_hash(
            'recipient_id2', 'email_subject2', 'email_html_body2')
        self.assertNotEqual(email_hash1, email_hash2)
        # pylint: enable=protected-access
