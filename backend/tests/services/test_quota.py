import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import HTTPException
from app.models.user import User, PlanType
from app.services.quota import get_effective_plan, check_competitor_quota, PLAN_COMPETITOR_QUOTAS

class TestQuotaService(unittest.TestCase):

    def test_get_effective_plan_starter(self):
        user = User(email="test@example.com", hashed_password="pw", plan_type=PlanType.STARTER)
        self.assertEqual(get_effective_plan(user), PlanType.STARTER)

    def test_get_effective_plan_ultimate(self):
        user = User(email="test@example.com", hashed_password="pw", plan_type=PlanType.ULTIMATE)
        self.assertEqual(get_effective_plan(user), PlanType.ULTIMATE)

    def test_get_effective_plan_growth_in_trial(self):
        user = User(
            email="test@example.com", 
            hashed_password="pw", 
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.utcnow() - timedelta(days=6),
            is_paid=False
        )
        self.assertEqual(get_effective_plan(user), PlanType.GROWTH)

    def test_get_effective_plan_growth_trial_expired_unpaid(self):
        user = User(
            email="test@example.com", 
            hashed_password="pw", 
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.utcnow() - timedelta(days=8),
            is_paid=False
        )
        self.assertEqual(get_effective_plan(user), PlanType.STARTER)

    def test_get_effective_plan_growth_trial_expired_paid(self):
        user = User(
            email="test@example.com", 
            hashed_password="pw", 
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.utcnow() - timedelta(days=8),
            is_paid=True
        )
        self.assertEqual(get_effective_plan(user), PlanType.GROWTH)

    def test_check_competitor_quota_under_limit(self):
        user = User(email="test@example.com", hashed_password="pw", plan_type=PlanType.STARTER)
        db = MagicMock()
        
        # Mocking the chain: db.exec(statement).one()
        mock_exec = MagicMock()
        db.exec.return_value = mock_exec
        mock_exec.one.return_value = 2  # Current count 2, limit is 3 for Starter
        
        try:
            check_competitor_quota(user, db)
        except HTTPException:
            self.fail("check_competitor_quota raised HTTPException unexpectedly!")

    def test_check_competitor_quota_at_limit(self):
        user = User(email="test@example.com", hashed_password="pw", plan_type=PlanType.STARTER)
        db = MagicMock()
        
        mock_exec = MagicMock()
        db.exec.return_value = mock_exec
        mock_exec.one.return_value = 3  # Current count 3, limit is 3
        
        with self.assertRaises(HTTPException) as cm:
            check_competitor_quota(user, db)
        self.assertEqual(cm.exception.status_code, 403)

    def test_check_competitor_quota_over_limit(self):
        user = User(email="test@example.com", hashed_password="pw", plan_type=PlanType.STARTER)
        db = MagicMock()
        
        mock_exec = MagicMock()
        db.exec.return_value = mock_exec
        mock_exec.one.return_value = 4  # Current count 4, limit is 3
        
        with self.assertRaises(HTTPException) as cm:
            check_competitor_quota(user, db)
        self.assertEqual(cm.exception.status_code, 403)

if __name__ == '__main__':
    unittest.main()
