# registration/tests/test_comments.py

from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import (
    CustomUser
)
from registration.models import (
    RegistrationComment,
    CommentType,
)
from fairs.models import (
    Fair,
)
from registration.factories import (
    UserFactory
)

class CreateRegistrationCommentManagerTest(TestCase):

    fixtures = ['accounts.yaml', 'authgroups.yaml']

    def setUp(self):
        # Create a test user
        self.user = UserFactory()

    def test_create_comment(self):
        # Create a dummy stallholder, comment_type, and fair for testing
        test_comment = "Stall registration ID " + str(65) + (
            ' will need to be reviewed by the convener '
            'because:\n')
        test_comment = test_comment + '- the food certificate is not valid for the period of the fair.'
        stallholder = CustomUser.objects.all().get(email='thehungrymonkey.wellington@gmail.com')
        comment_type = CommentType.objects.create(type_name='Test Comment Type')
        fair = Fair.objects.create(fair_name='Test Fair', activation_date=timezone.now())

        # Call the manager's create_comment method
        comment = RegistrationComment.createregistrationcommentmgr.create_comment(
            stallholder=stallholder,
            current_fair=fair,
            comment_type=comment_type,
            comment=test_comment
        )

        # Check if the comment has been created correctly
        self.assertEqual(comment.stallholder, stallholder)
        self.assertEqual(comment.comment_type, comment_type)
        self.assertEqual(comment.comment,test_comment)
        self.assertEqual(comment.fair, fair)
        self.assertFalse(comment.is_done)  # Assuming is_done default is False

        # You can add more assertions based on your model fields

    def tearDown(self):
        # Clean up any created objects in the database
        get_user_model().objects.all().delete()
        CustomUser.objects.all().delete()
        CommentType.objects.all().delete()
        Fair.objects.all().delete()
        RegistrationComment.objects.all().delete()
from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import CustomUser
from registration.models import RegistrationComment, CommentType
from fairs.models import Fair
from registration.factories import UserFactory

class CreateRegistrationCommentManagerTest(TestCase):

    fixtures = ['accounts.yaml', 'authgroups.yaml']

    def setUp(self):
        # Ensure the database is clean before each test
        self.tearDown()
        # Create a test user
        self.user = UserFactory()

    def test_create_comment(self):
        # Create a dummy stallholder, comment_type, and fair for testing
        test_comment = (
            "Stall registration ID 65 will need to be reviewed by the convener "
            "because:\n- the food certificate is not valid for the period of the fair."
        )
        stallholder = CustomUser.objects.create_user(
            username='unique_stallholder_username',
            email='thehungrymonkey.wellington@gmail.com',
            password='testpassword'
        )
        comment_type = CommentType.objects.create(type_name='Test Comment Type')
        fair = Fair.objects.create(fair_name='Test Fair', activation_date=timezone.now())

        # Call the manager's create_comment method
        comment = RegistrationComment.createregistrationcommentmgr.create_comment(
            stallholder=stallholder,
            current_fair=fair,
            comment_type=comment_type,
            comment=test_comment
        )

        # Check if the comment has been created correctly
        self.assertEqual(comment.stallholder, stallholder)
        self.assertEqual(comment.comment_type, comment_type)
        self.assertEqual(comment.comment, test_comment)
        self.assertEqual(comment.fair, fair)
        self.assertFalse(comment.is_done)  # Assuming is_done default is False

    def tearDown(self):
        # Clean up any created objects in the database
        get_user_model().objects.all().delete()
        CustomUser.objects.all().delete()
        CommentType.objects.all().delete()
        Fair.objects.all().delete()
        RegistrationComment.objects.all().delete()
