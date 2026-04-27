# Copyright 2025 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest.mock import MagicMock

from toxicity_guardrail import ToxicityGuardrailStep


class TestToxicityGuardrailStep:
    def _make_step(self, threshold=0.5):
        step = ToxicityGuardrailStep(threshold=threshold)
        step._classifier = MagicMock()
        return step

    def test_safe_input_passes(self):
        step = self._make_step()
        step._classifier.return_value = [{"label": "non-toxic", "score": 0.999}]
        event = {"question": "What is the capital of France?"}
        result = step.do(event)
        assert result == event

    def test_toxic_input_blocked(self):
        step = self._make_step()
        step._classifier.return_value = [{"label": "toxic", "score": 0.998}]
        event = {"question": "some clearly toxic text"}
        try:
            step.do(event)
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Request blocked" in str(e)
            assert "0.998" in str(e)

    def test_custom_threshold_passes_below(self):
        step = self._make_step(threshold=0.9)
        # Score 0.85 < threshold 0.9 — should pass through
        step._classifier.return_value = [{"label": "toxic", "score": 0.85}]
        event = {"question": "borderline content"}
        result = step.do(event)
        assert result == event

    def test_score_at_threshold_is_blocked(self):
        step = self._make_step(threshold=0.5)
        # Score exactly equal to threshold — should be blocked
        step._classifier.return_value = [{"label": "toxic", "score": 0.5}]
        event = {"question": "borderline content"}
        try:
            step.do(event)
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "0.500" in str(e)

    def test_non_toxic_label_inverts_score(self):
        step = self._make_step(threshold=0.5)
        # label="non-toxic", score=0.99 → toxicity score = 1 - 0.99 = 0.01 → safe
        step._classifier.return_value = [{"label": "non-toxic", "score": 0.99}]
        event = {"question": "a perfectly safe question"}
        result = step.do(event)
        assert result == event

    def test_empty_question_is_safe(self):
        step = self._make_step()
        step._classifier.return_value = [{"label": "non-toxic", "score": 0.999}]
        event = {"question": ""}
        result = step.do(event)
        assert result == event

    def test_event_passthrough_unchanged(self):
        step = self._make_step()
        step._classifier.return_value = [{"label": "non-toxic", "score": 0.99}]
        event = {"question": "Hello world", "extra_field": 42}
        result = step.do(event)
        assert result["extra_field"] == 42
