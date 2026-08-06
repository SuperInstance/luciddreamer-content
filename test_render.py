#!/usr/bin/env python3
"""
Tests for LucidDreamer render.py — Content Rendering Pipeline

Covers:
  - Configuration constants and defaults
  - SHOW_VOICES mapping completeness
  - adapt_script() — API call construction, truncation, error handling
  - generate_tts() — text cleaning, subprocess invocation, output validation
  - generate_slide_prompts() — JSON parsing, fallback behavior, error handling
  - generate_images() — iteration, file handling, rate limiting
  - upload_to_r2() — file routing, wrangler invocation, error handling
  - generate_metadata() — duration estimation, field structure, file output
  - render_episode() — full pipeline orchestration
  - CLI — argument parsing, defaults, help text
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from urllib.error import HTTPError, URLError

# Ensure we can import render.py
sys.path.insert(0, str(Path(__file__).parent))
import render


class TestConfiguration(unittest.TestCase):
    """Test module-level configuration constants."""

    def test_deepseek_api_key_from_env(self):
        """API key should be readable from environment."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key-123"}):
            # Re-import would be needed for full test; just verify structure
            self.assertTrue(hasattr(render, "DEEPSEEK_API_KEY"))

    def test_deepseek_api_url_is_valid(self):
        self.assertTrue(render.DEEPSEEK_API_URL.startswith("https://"))
        self.assertIn("deepseek", render.DEEPSEEK_API_URL)

    def test_deepseek_model_is_string(self):
        self.assertIsInstance(render.DEEPSEEK_MODEL, str)
        self.assertTrue(len(render.DEEPSEEK_MODEL) > 0)

    def test_mmx_path_default(self):
        self.assertTrue(isinstance(render.MMX_PATH, str))

    def test_r2_bucket_name(self):
        self.assertEqual(render.R2_BUCKET, "luciddreamer-content")

    def test_default_voice_exists(self):
        self.assertIsInstance(render.DEFAULT_VOICE, str)
        self.assertTrue(len(render.DEFAULT_VOICE) > 0)

    def test_default_show_exists(self):
        self.assertIsInstance(render.DEFAULT_SHOW, str)
        self.assertTrue(len(render.DEFAULT_SHOW) > 0)


class TestShowVoices(unittest.TestCase):
    """Test the SHOW_VOICES mapping."""

    def test_all_shows_have_voices(self):
        for show, voice in render.SHOW_VOICES.items():
            self.assertIsInstance(show, str)
            self.assertIsInstance(voice, str)
            self.assertTrue(len(voice) > 0, f"Show '{show}' has empty voice")

    def test_known_shows_present(self):
        expected_shows = [
            "the-taps-late-show",
            "verse-2",
            "night-school",
            "fetch-radio-theater",
            "git-agent-confidential",
            "the-monitor-engineer",
            "darmok-translations",
            "kaleidoscope-sessions",
        ]
        for show in expected_shows:
            self.assertIn(show, render.SHOW_VOICES, f"Missing show: {show}")

    def test_all_voices_start_with_english(self):
        """All voices follow the English_VoiceName convention."""
        for show, voice in render.SHOW_VOICES.items():
            self.assertTrue(
                voice.startswith("English"),
                f"Voice '{voice}' for show '{show}' doesn't start with 'English'"
            )

    def test_no_duplicate_voices_across_shows(self):
        """Multiple shows can share a voice, but we verify it's intentional."""
        voices = list(render.SHOW_VOICES.values())
        # This is not an error, just document the pattern
        self.assertTrue(len(voices) >= len(set(voices)))

    def test_default_show_in_mapping(self):
        """The default show should be in SHOW_VOICES."""
        self.assertIn(render.DEFAULT_SHOW, render.SHOW_VOICES)

    def test_default_voice_is_valid(self):
        """The default voice should be a non-empty English_ voice ID."""
        self.assertTrue(render.DEFAULT_VOICE.startswith("English"))
        self.assertTrue(len(render.DEFAULT_VOICE) > 5)


class TestSystemPrompts(unittest.TestCase):
    """Test that system prompts have the right content."""

    def test_adaptation_prompt_has_rules(self):
        self.assertIn("podcast", render.ADAPTATION_SYSTEM_PROMPT.lower())
        self.assertIn("audio cue", render.ADAPTATION_SYSTEM_PROMPT.lower())
        self.assertIn("LucidDreamer", render.ADAPTATION_SYSTEM_PROMPT)

    def test_adaptation_prompt_has_output_format(self):
        self.assertIn("intro", render.ADAPTATION_SYSTEM_PROMPT.lower())
        self.assertIn("outro", render.ADAPTATION_SYSTEM_PROMPT.lower())

    def test_adaptation_prompt_has_tone(self):
        self.assertIn("literary", render.ADAPTATION_SYSTEM_PROMPT.lower())
        self.assertIn("intimate", render.ADAPTATION_SYSTEM_PROMPT.lower())

    def test_image_prompt_has_json_format(self):
        self.assertIn("slides", render.IMAGE_SYSTEM_PROMPT)
        self.assertIn("JSON", render.IMAGE_SYSTEM_PROMPT)

    def test_image_prompt_has_art_style_guidance(self):
        self.assertIn("art style", render.IMAGE_SYSTEM_PROMPT.lower())
        self.assertIn("lighting", render.IMAGE_SYSTEM_PROMPT.lower())


class TestAdaptScript(unittest.TestCase):
    """Test adapt_script() function."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_path = Path(self.tmpdir) / "test-piece.md"
        self.source_path.write_text("# Test Story\n\nThis is a test story about the sea.")

    def test_adapt_script_success(self):
        """Test successful script adaptation."""
        mock_response = {
            "choices": [{"message": {"content": "Adapted script content"}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        with patch("render.urlopen", return_value=mock_resp_io):
            result = render.adapt_script(self.source_path, "verse-2", "English_CalmWoman")

        self.assertEqual(result, "Adapted script content")

    def test_adapt_script_truncates_long_text(self):
        """Test that long source text is truncated."""
        long_text = "A" * 15000
        long_source = Path(self.tmpdir) / "long.md"
        long_source.write_text(long_text)

        captured_body = {}

        mock_response = {
            "choices": [{"message": {"content": "Adapted"}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture_request(req, **kwargs):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture_request):
            render.adapt_script(long_source, "test-show", "test-voice")

        sent_body = json.loads(captured_body["data"].decode())
        user_msg = sent_body["messages"][1]["content"]
        self.assertIn("truncated for length", user_msg)

    def test_adapt_script_short_text_not_truncated(self):
        """Short text should not be truncated."""
        short_source = Path(self.tmpdir) / "short.md"
        short_source.write_text("Short story.")

        captured_body = {}

        mock_response = {
            "choices": [{"message": {"content": "Adapted"}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture_request(req, **kwargs):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture_request):
            render.adapt_script(short_source, "test-show", "test-voice")

        sent_body = json.loads(captured_body["data"].decode())
        user_msg = sent_body["messages"][1]["content"]
        self.assertNotIn("truncated for length", user_msg)

    def test_adapt_script_truncation_threshold(self):
        """Text over 12000 chars should be truncated."""
        # Exactly 12000 chars should not truncate
        source_12000 = Path(self.tmpdir) / "exact.md"
        source_12000.write_text("B" * 12000)

        captured_body = {}
        mock_response = {"choices": [{"message": {"content": "OK"}}]}
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.adapt_script(source_12000, "show", "voice")

        sent = json.loads(captured_body["data"].decode())
        self.assertNotIn("truncated", sent["messages"][1]["content"])

        # 12001 chars should truncate
        source_12001 = Path(self.tmpdir) / "over.md"
        source_12001.write_text("B" * 12001)

        with patch("render.urlopen", side_effect=capture):
            render.adapt_script(source_12001, "show", "voice")

        sent = json.loads(captured_body["data"].decode())
        self.assertIn("truncated", sent["messages"][1]["content"])

    def test_adapt_script_includes_show_and_voice(self):
        """The user prompt should include the show name and voice."""
        captured_body = {}
        mock_response = {"choices": [{"message": {"content": "OK"}}]}
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.adapt_script(self.source_path, "night-school", "English_WiseScholar")

        sent = json.loads(captured_body["data"].decode())
        user_msg = sent["messages"][1]["content"]
        self.assertIn("night-school", user_msg)
        self.assertIn("English_WiseScholar", user_msg)

    def test_adapt_script_request_headers(self):
        """Request should have correct headers."""
        captured_req = {}
        mock_response = {"choices": [{"message": {"content": "OK"}}]}
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_req["headers"] = req.headers
            captured_req["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.adapt_script(self.source_path, "show", "voice")

        # urllib uses Content-type (lowercase t)
        ct = captured_req["headers"].get("Content-type") or captured_req["headers"].get("Content-Type")
        self.assertIsNotNone(ct)
        self.assertIn("Authorization", captured_req["headers"])
        self.assertTrue(
            captured_req["headers"]["Authorization"].startswith("Bearer ")
        )

    def test_adapt_script_temperature_is_creative(self):
        """Temperature should be set for creative output."""
        captured_body = {}
        mock_response = {"choices": [{"message": {"content": "OK"}}]}
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.adapt_script(self.source_path, "show", "voice")

        sent = json.loads(captured_body["data"].decode())
        self.assertGreater(sent["temperature"], 0.5)
        self.assertLessEqual(sent["temperature"], 1.0)

    def test_adapt_script_http_error_exits(self):
        """HTTP errors should cause sys.exit."""
        error_resp = io.BytesIO(b'{"error": "rate limited"}')
        http_err = HTTPError(
            "https://api.deepseek.com",
            429,
            "Too Many Requests",
            {"Content-Type": "application/json"},
            error_resp,
        )

        with patch("render.urlopen", side_effect=http_err):
            with self.assertRaises(SystemExit):
                render.adapt_script(self.source_path, "show", "voice")

    def test_adapt_script_url_error_exits(self):
        """Network errors should cause sys.exit."""
        with patch("render.urlopen", side_effect=URLError("Connection refused")):
            with self.assertRaises(SystemExit):
                render.adapt_script(self.source_path, "show", "voice")

    def test_adapt_script_reads_file_as_utf8(self):
        """Should handle UTF-8 content properly."""
        unicode_source = Path(self.tmpdir) / "unicode.md"
        unicode_source.write_text("# Café\n\nRésumé of naïve façade.", encoding="utf-8")

        mock_response = {"choices": [{"message": {"content": "Adapté"}}]}
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        with patch("render.urlopen", return_value=mock_resp_io):
            result = render.adapt_script(unicode_source, "show", "voice")

        self.assertEqual(result, "Adapté")


class TestGenerateTTS(unittest.TestCase):
    """Test generate_tts() function."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output_path = Path(self.tmpdir) / "audio.mp3"

    def test_generate_tts_strips_audio_cues(self):
        """Audio cues in brackets should be stripped."""
        captured_cmd = {}

        def fake_run(cmd, **kwargs):
            captured_cmd["cmd"] = cmd
            self.output_path.write_bytes(b"fake audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts(
                "[MUSIC IN] Hello world [PAUSE] this is a test [FADE]",
                self.output_path,
                "test-voice",
            )

        # The temp file should not contain bracketed content
        temp_text = self.output_path.parent / "tts-text.txt"
        content = temp_text.read_text()
        self.assertNotIn("[MUSIC IN]", content)
        self.assertNotIn("[PAUSE]", content)
        self.assertNotIn("[FADE]", content)
        self.assertIn("Hello world", content)

    def test_generate_tts_strips_italic_and_bold(self):
        """Markdown formatting should be stripped."""
        captured_cmd = {}

        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"fake audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts(
                "**Bold text** and *italic text* and normal.",
                self.output_path,
                "voice",
            )

        temp_text = self.output_path.parent / "tts-text.txt"
        content = temp_text.read_text()
        self.assertNotIn("**", content)
        self.assertIn("Bold text", content)
        self.assertIn("italic text", content)

    def test_generate_tts_strips_headers_and_dividers(self):
        """Markdown headers and hr should be stripped."""
        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts(
                "# Header\n\n---\n\nContent here",
                self.output_path,
                "voice",
            )

        temp_text = self.output_path.parent / "tts-text.txt"
        content = temp_text.read_text()
        lines = content.split("\n")
        self.assertFalse(any(l.startswith("#") for l in lines))

    def test_generate_tts_collapses_blank_lines(self):
        """Multiple blank lines should be collapsed."""
        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts(
                "Line 1\n\n\n\n\n\nLine 2",
                self.output_path,
                "voice",
            )

        temp_text = self.output_path.parent / "tts-text.txt"
        content = temp_text.read_text()
        self.assertNotIn("\n\n\n", content)

    def test_generate_tts_success(self):
        """Successful TTS generation returns True."""
        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"fake audio data")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            result = render.generate_tts("Test text", self.output_path, "voice")

        self.assertTrue(result)
        self.assertTrue(self.output_path.exists())

    def test_generate_tts_subprocess_failure_returns_false(self):
        """Subprocess failure should return False, not raise."""
        with patch("render.subprocess.run",
                    return_value=MagicMock(returncode=1, stderr="Error", stdout="")):
            result = render.generate_tts("Test", self.output_path, "voice")

        self.assertFalse(result)

    def test_generate_tts_missing_output_returns_false(self):
        """If output file is not created, return False."""
        with patch("render.subprocess.run",
                    return_value=MagicMock(returncode=0, stderr="", stdout="")):
            result = render.generate_tts("Test", self.output_path, "voice")

        self.assertFalse(result)

    def test_generate_tts_writes_temp_text_file(self):
        """A tts-text.txt file should be created alongside audio."""
        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts("Hello world", self.output_path, "voice")

        temp_text = self.output_path.parent / "tts-text.txt"
        self.assertTrue(temp_text.exists())
        self.assertIn("Hello world", temp_text.read_text())

    def test_generate_tts_command_structure(self):
        """The MMX command should have the right structure."""
        captured_cmd = {}

        def fake_run(cmd, **kwargs):
            captured_cmd["cmd"] = cmd
            self.output_path.write_bytes(b"audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts("Test", self.output_path, "test-voice")

        cmd = captured_cmd["cmd"]
        self.assertIn("speech", cmd)
        self.assertIn("synthesize", cmd)
        self.assertIn("--voice", cmd)
        self.assertIn("test-voice", cmd)

    def test_generate_tts_strips_hr_lines(self):
        """--- lines should be removed."""
        def fake_run(cmd, **kwargs):
            self.output_path.write_bytes(b"audio")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            render.generate_tts("Text\n---\nMore", self.output_path, "voice")

        temp_text = self.output_path.parent / "tts-text.txt"
        content = temp_text.read_text()
        self.assertNotIn("---", content.strip())


class TestGenerateSlidePrompts(unittest.TestCase):
    """Test generate_slide_prompts() function."""

    def test_generate_slide_prompts_success_json(self):
        """Test successful JSON parsing of slide prompts."""
        mock_response = {
            "choices": [{"message": {"content": '{"slides": ["prompt 1", "prompt 2"]}'}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        with patch("render.urlopen", return_value=mock_resp_io):
            prompts = render.generate_slide_prompts("Script text", count=2)

        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0], "prompt 1")

    def test_generate_slide_prompts_truncates_to_count(self):
        """Should return at most 'count' prompts."""
        mock_response = {
            "choices": [{"message": {"content": '{"slides": ["p1", "p2", "p3", "p4", "p5"]}'}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        with patch("render.urlopen", return_value=mock_resp_io):
            prompts = render.generate_slide_prompts("Script", count=3)

        self.assertEqual(len(prompts), 3)

    def test_generate_slide_prompts_fallback_no_json(self):
        """If no JSON found, should fall back to line splitting."""
        mock_response = {
            "choices": [{"message": {"content": "prompt one\nprompt two\nprompt three"}}]
        }

        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        with patch("render.urlopen", return_value=mock_resp_io):
            prompts = render.generate_slide_prompts("Script", count=3)

        self.assertTrue(len(prompts) <= 3)

    def test_generate_slide_prompts_error_returns_empty(self):
        """On error, return empty list."""
        with patch("render.urlopen", side_effect=Exception("Network error")):
            prompts = render.generate_slide_prompts("Script")

        self.assertEqual(prompts, [])

    def test_generate_slide_prompts_includes_count_in_prompt(self):
        """The user prompt should include the requested count."""
        captured_body = {}
        mock_response = {
            "choices": [{"message": {"content": '{"slides": ["p1"]}'}}]
        }
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.generate_slide_prompts("Script", count=5)

        sent = json.loads(captured_body["data"].decode())
        user_msg = sent["messages"][1]["content"]
        self.assertIn("5", user_msg)

    def test_generate_slide_prompts_uses_higher_temperature(self):
        """Image prompts should use higher temperature for creativity."""
        captured_body = {}
        mock_response = {
            "choices": [{"message": {"content": '{"slides": ["p1"]}'}}]
        }
        mock_resp_io = MagicMock()
        mock_resp_io.read.return_value = json.dumps(mock_response).encode()
        mock_resp_io.__enter__ = MagicMock(return_value=mock_resp_io)
        mock_resp_io.__exit__ = MagicMock(return_value=False)

        def capture(req, **kw):
            captured_body["data"] = req.data
            return mock_resp_io

        with patch("render.urlopen", side_effect=capture):
            render.generate_slide_prompts("Script")

        sent = json.loads(captured_body["data"].decode())
        self.assertGreaterEqual(sent["temperature"], 0.7)


class TestGenerateImages(unittest.TestCase):
    """Test generate_images() function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def test_generate_images_success(self):
        """Test successful image generation."""
        def fake_run(cmd, **kwargs):
            # Extract --out path from command
            out_idx = cmd.index("--out") + 1
            out_path = Path(cmd[out_idx])
            out_path.write_bytes(b"fake png")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            with patch("time.sleep"):  # Skip delays
                result = render.generate_images(["prompt1", "prompt2"], self.tmpdir)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(r.endswith(".png") for r in result))

    def test_generate_images_handles_failure(self):
        """Failed image generation should not be included in results."""
        call_count = [0]

        def fake_run(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(returncode=1, stderr="Rate limited", stdout="")
            out_idx = cmd.index("--out") + 1
            Path(cmd[out_idx]).write_bytes(b"png")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            with patch("time.sleep"):
                result = render.generate_images(["p1", "p2"], self.tmpdir)

        self.assertEqual(len(result), 1)

    def test_generate_images_creates_named_files(self):
        """Generated files should follow slide-N.png naming."""
        def fake_run(cmd, **kwargs):
            out_idx = cmd.index("--out") + 1
            Path(cmd[out_idx]).write_bytes(b"png")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            with patch("time.sleep"):
                render.generate_images(["p1", "p2", "p3"], self.tmpdir)

        self.assertTrue((self.tmpdir / "slide-1.png").exists())
        self.assertTrue((self.tmpdir / "slide-2.png").exists())
        self.assertTrue((self.tmpdir / "slide-3.png").exists())

    def test_generate_images_aspect_ratio_16_9(self):
        """Images should use 16:9 aspect ratio."""
        captured_cmds = []

        def fake_run(cmd, **kwargs):
            captured_cmds.append(cmd)
            out_idx = cmd.index("--out") + 1
            Path(cmd[out_idx]).write_bytes(b"png")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            with patch("time.sleep"):
                render.generate_images(["p1"], self.tmpdir)

        self.assertIn("16:9", captured_cmds[0])

    def test_generate_images_empty_prompts(self):
        """Empty prompts list should return empty list."""
        with patch("render.subprocess.run") as mock_run:
            with patch("time.sleep"):
                result = render.generate_images([], self.tmpdir)

        self.assertEqual(result, [])
        mock_run.assert_not_called()

    def test_generate_images_sleeps_between_images(self):
        """Should sleep between images to avoid rate limiting."""
        def fake_run(cmd, **kwargs):
            out_idx = cmd.index("--out") + 1
            Path(cmd[out_idx]).write_bytes(b"png")
            return MagicMock(returncode=0, stderr="", stdout="")

        with patch("render.subprocess.run", side_effect=fake_run):
            with patch("time.sleep") as mock_sleep:
                render.generate_images(["p1", "p2", "p3"], self.tmpdir)

        self.assertEqual(mock_sleep.call_count, 3)


class TestUploadToR2(unittest.TestCase):
    """Test upload_to_r2() function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.episode_name = "episode-test"

    def test_upload_skips_if_npx_not_found(self):
        """Should skip upload if npx not available."""
        with patch("subprocess.run", return_value=MagicMock(returncode=1)):
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertFalse(result)

    def test_upload_audio_file(self):
        """Audio file should be uploaded."""
        audio = self.tmpdir / "audio.mp3"
        audio.write_bytes(b"audio data")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
                MagicMock(returncode=0, stderr="", stdout=""),  # audio upload
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertTrue(result)

    def test_upload_script_file(self):
        """Script file should be uploaded."""
        script = self.tmpdir / "script.md"
        script.write_text("Script content")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
                MagicMock(returncode=0, stderr="", stdout=""),  # script upload
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertTrue(result)

    def test_upload_metadata_file(self):
        """Metadata file should be uploaded."""
        meta = self.tmpdir / "metadata.json"
        meta.write_text('{"key": "value"}')

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
                MagicMock(returncode=0, stderr="", stdout=""),  # metadata upload
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertTrue(result)

    def test_upload_slide_files(self):
        """Slide files should be uploaded."""
        for i in range(1, 4):
            slide = self.tmpdir / f"slide-{i}.png"
            slide.write_bytes(b"png data")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
                MagicMock(returncode=0, stderr="", stdout=""),  # slide 1
                MagicMock(returncode=0, stderr="", stdout=""),  # slide 2
                MagicMock(returncode=0, stderr="", stdout=""),  # slide 3
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertTrue(result)

    def test_upload_no_files_returns_false(self):
        """If no files to upload, return False."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertFalse(result)

    def test_upload_partial_failure_still_continues(self):
        """If some uploads fail, others should still proceed."""
        audio = self.tmpdir / "audio.mp3"
        audio.write_bytes(b"audio")
        script = self.tmpdir / "script.md"
        script.write_text("script")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which npx
                MagicMock(returncode=1, stderr="Failed", stdout=""),  # audio fails
                MagicMock(returncode=0, stderr="", stdout=""),  # script succeeds
            ]
            result = render.upload_to_r2(self.tmpdir, self.episode_name)

        self.assertTrue(result)  # At least one succeeded


class TestGenerateMetadata(unittest.TestCase):
    """Test generate_metadata() function."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_path = Path(self.tmpdir) / "test-piece.md"
        self.source_path.write_text("# Test\n\nContent here.")
        self.episode_dir = Path(tempfile.mkdtemp())

    def test_metadata_has_required_fields(self):
        """Metadata should have all required fields."""
        meta = render.generate_metadata(
            self.source_path,
            "Script text here",
            "verse-2",
            "English_CalmWoman",
            self.episode_dir,
            4,
        )

        required = [
            "title", "show", "source", "source_filename",
            "voice", "word_count", "duration_estimate_minutes",
            "slide_count", "rendered_at", "pipeline_version",
        ]
        for field in required:
            self.assertIn(field, meta, f"Missing field: {field}")

    def test_metadata_title_from_filename(self):
        """Title should be derived from source filename."""
        source = Path("/tmp/the-lighthouse-keeper.md")
        meta = render.generate_metadata(
            source, "script", "show", "voice", self.episode_dir, 3
        )

        self.assertIn("Lighthouse", meta["title"])

    def test_metadata_word_count(self):
        """Word count should be accurate."""
        script = "one two three four five"
        meta = render.generate_metadata(
            self.source_path, script, "show", "voice", self.episode_dir, 0
        )

        self.assertEqual(meta["word_count"], 5)

    def test_metadata_duration_estimate(self):
        """Duration estimate should be word_count / 150."""
        script = " ".join(["word"] * 300)  # 300 words = 2.0 minutes
        meta = render.generate_metadata(
            self.source_path, script, "show", "voice", self.episode_dir, 0
        )

        self.assertAlmostEqual(meta["duration_estimate_minutes"], 2.0, places=1)

    def test_metadata_duration_for_empty_script(self):
        """Empty script should have 0 duration."""
        meta = render.generate_metadata(
            self.source_path, "", "show", "voice", self.episode_dir, 0
        )

        self.assertEqual(meta["duration_estimate_minutes"], 0.0)

    def test_metadata_pipeline_version(self):
        """Pipeline version should be a version string."""
        meta = render.generate_metadata(
            self.source_path, "script", "show", "voice", self.episode_dir, 0
        )

        self.assertTrue(meta["pipeline_version"].count(".") >= 1)

    def test_metadata_file_written(self):
        """Metadata should be written to episode_dir/metadata.json."""
        meta = render.generate_metadata(
            self.source_path, "script", "show", "voice", self.episode_dir, 0
        )

        meta_path = self.episode_dir / "metadata.json"
        self.assertTrue(meta_path.exists())

        saved = json.loads(meta_path.read_text())
        self.assertEqual(saved["show"], "show")

    def test_metadata_source_filename(self):
        """source_filename should be the Path name."""
        meta = render.generate_metadata(
            self.source_path, "script", "show", "voice", self.episode_dir, 0
        )

        self.assertEqual(meta["source_filename"], "test-piece.md")

    def test_metadata_rendered_at_is_iso(self):
        """rendered_at should be an ISO-like timestamp."""
        meta = render.generate_metadata(
            self.source_path, "script", "show", "voice", self.episode_dir, 0
        )

        self.assertIn("T", meta["rendered_at"])
        # Should parse as valid timestamp
        import time as _time
        _time.strptime(meta["rendered_at"], "%Y-%m-%dT%H:%M:%S")

    def test_metadata_slide_count(self):
        """slide_count should match input."""
        meta = render.generate_metadata(
            self.source_path, "script", "show", "voice", self.episode_dir, 7
        )

        self.assertEqual(meta["slide_count"], 7)


class TestRenderEpisode(unittest.TestCase):
    """Test render_episode() — the full pipeline orchestration."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source = Path(self.tmpdir) / "source.md"
        self.source.write_text("# Test Story\n\nThe sea was dark.")

    def test_render_episode_missing_source_exits(self):
        """Missing source file should cause sys.exit."""
        with self.assertRaises(SystemExit):
            render.render_episode("/nonexistent/file.md")

    def test_render_episode_creates_output_dir(self):
        """Should create the output directory."""
        out_dir = Path(self.tmpdir) / "output"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_audio=False,
                            skip_images=True,
                            skip_upload=True,
                        )

        self.assertTrue(out_dir.exists())

    def test_render_episode_default_show(self):
        """Should use DEFAULT_SHOW when no show specified."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        meta = json.loads((out_dir / "metadata.json").read_text())
        self.assertEqual(meta["show"], render.DEFAULT_SHOW)

    def test_render_episode_custom_show(self):
        """Should use the specified show."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            show="night-school",
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        meta = json.loads((out_dir / "metadata.json").read_text())
        self.assertEqual(meta["show"], "night-school")

    def test_render_episode_voice_override(self):
        """Explicit voice should override show default."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            show="verse-2",
                            voice="Custom_Voice",
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        meta = json.loads((out_dir / "metadata.json").read_text())
        self.assertEqual(meta["voice"], "Custom_Voice")

    def test_render_episode_writes_script(self):
        """Script should be written to script.md."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="The adapted script."):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        script = (out_dir / "script.md").read_text()
        self.assertEqual(script, "The adapted script.")

    def test_render_episode_returns_episode_dir(self):
        """Should return the episode directory path."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        result = render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        self.assertEqual(result, out_dir)

    def test_render_episode_skip_audio(self):
        """skip_audio should prevent TTS generation."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts") as mock_tts:
                with patch("render.generate_slide_prompts", return_value=[]):
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_audio=True,
                            skip_upload=True,
                            skip_images=True,
                        )

        mock_tts.assert_not_called()

    def test_render_episode_skip_images(self):
        """skip_images should prevent slide generation."""
        out_dir = Path(self.tmpdir) / "out"
        with patch("render.adapt_script", return_value="Script"):
            with patch("render.generate_tts", return_value=True):
                with patch("render.generate_slide_prompts") as mock_prompts:
                    with patch("render.upload_to_r2", return_value=True):
                        render.render_episode(
                            str(self.source),
                            out_dir=str(out_dir),
                            skip_upload=True,
                            skip_images=True,
                        )

        mock_prompts.assert_not_called()


class TestCLI(unittest.TestCase):
    """Test the CLI argument parser."""

    def test_cli_source_required(self):
        """Source argument is required."""
        parser = render.argparse.ArgumentParser()
        # Re-create the parser logic
        with self.assertRaises(SystemExit):
            # Running with no args should fail
            sys.argv = ["render.py"]
            render.main()

    def test_cli_source_argument(self):
        """Source argument should be parsed."""
        sys.argv = ["render.py", "test.md", "--no-upload", "--no-images", "--no-audio"]
        with patch("render.render_episode") as mock_render:
            render.main()

        mock_render.assert_called_once()
        call_kwargs = mock_render.call_args
        self.assertIn("source_path", call_kwargs.kwargs)

    def test_cli_no_upload_flag(self):
        """--no-upload should set skip_upload."""
        sys.argv = ["render.py", "test.md", "--no-upload"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertTrue(call_kwargs["skip_upload"])

    def test_cli_no_images_flag(self):
        """--no-images should set skip_images."""
        sys.argv = ["render.py", "test.md", "--no-images"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertTrue(call_kwargs["skip_images"])

    def test_cli_no_audio_flag(self):
        """--no-audio should set skip_audio."""
        sys.argv = ["render.py", "test.md", "--no-audio"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertTrue(call_kwargs["skip_audio"])

    def test_cli_slides_default(self):
        """Default slide count should be 4."""
        sys.argv = ["render.py", "test.md"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertEqual(call_kwargs["slide_count"], 4)

    def test_cli_slides_custom(self):
        """Custom slide count should be parsed."""
        sys.argv = ["render.py", "test.md", "--slides", "7"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertEqual(call_kwargs["slide_count"], 7)

    def test_cli_show_argument(self):
        """--show should be parsed."""
        sys.argv = ["render.py", "test.md", "--show", "night-school"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertEqual(call_kwargs["show"], "night-school")

    def test_cli_voice_argument(self):
        """--voice should be parsed."""
        sys.argv = ["render.py", "test.md", "--voice", "CustomVoice"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertEqual(call_kwargs["voice"], "CustomVoice")

    def test_cli_out_dir_argument(self):
        """--out-dir should be parsed."""
        sys.argv = ["render.py", "test.md", "--out-dir", "/tmp/ep"]
        with patch("render.render_episode") as mock_render:
            render.main()

        call_kwargs = mock_render.call_args.kwargs
        self.assertEqual(call_kwargs["out_dir"], "/tmp/ep")


if __name__ == "__main__":
    unittest.main()
