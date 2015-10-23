from django.test import TestCase

import datetime
from django.utils import timezone
from polls.models import Question
from django.core.urlresolvers import reverse

def create_question(question_text, days, choice):
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text,
                                    pub_date=time)
    if choice:
        question.choices.create(choice_text="Hello", votes=0)

    return question

class QuestionViewTests(TestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions exist, display message.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Display questions with pub_date in the past.
        """
        create_question(question_text="Past", days=-30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a future pub_date should not be displayed.
        """
        create_question(question_text="Future", days=30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Only display past question.
        """
        create_question(question_text="Future", days=30, choice=True)
        create_question(question_text="Past", days=-30, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        Displays multiple questions.
        """
        create_question(question_text="Past1", days=-30, choice=True)
        create_question(question_text="Past2", days=-31, choice=True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past1>', '<Question: Past2>']
        )

    def test_index_view_with_question_without_choices(self):
        """
        Does not display questions without choices
        """
        create_question(question_text="Good question", days=-5, choice=False)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [],
        )

class QuestiondIndexDetailTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        Return 404 for a detail view of a question with a future
        pub_date
        """
        future_question = create_question(question_text="Future", days=5, choice=True)
        response = self.client.get(reverse('polls:detail',
                                    args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        Should return detail view of question with past pub_date
        """
        past_question = create_question(question_text="Past", days=-5, choice=True)
        response = self.client.get(reverse('polls:detail',
                                            args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)


class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions with
        pub_date in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions with
        pub_date older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions with
        pub_date within last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)
