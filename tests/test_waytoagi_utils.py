import unittest
from datetime import datetime

from scripts.update_news import (
    SH_TZ,
    block_text_and_link,
    clean_update_title,
    decode_escaped_json,
    extract_all_mention_doc_urls,
    extract_waytoagi_recent_updates_from_block_map,
    infer_shanghai_year_for_month_day,
    parse_md_heading,
    parse_ym_heading,
)


class WaytoAgiUtilsTests(unittest.TestCase):
    def test_parse_ym_heading(self):
        self.assertEqual(parse_ym_heading("2026 年 2 月"), (2026, 2))

    def test_parse_md_heading(self):
        self.assertEqual(parse_md_heading("2 月 9 日"), (2, 9))

    def test_clean_update_title(self):
        self.assertEqual(clean_update_title("《 》  AI  更新  测试  "), "AI 更新 测试")

    def test_decode_escaped_json(self):
        raw = '{\\"id\\":\\"x\\",\\"type\\":\\"mention_doc\\",\\"data\\":{\\"title\\":\\"历史更新\\"}}'
        obj = decode_escaped_json(raw)
        self.assertEqual(obj["data"]["title"], "历史更新")

    def test_infer_shanghai_year_for_month_day(self):
        now = datetime(2026, 1, 2, 10, 0, tzinfo=SH_TZ)
        self.assertEqual(infer_shanghai_year_for_month_day(now, 12, 31), 2025)
        self.assertEqual(infer_shanghai_year_for_month_day(now, 1, 1), 2026)

    def test_extract_recent_updates_from_block_map(self):
        now = datetime(2026, 2, 20, 10, 0, tzinfo=SH_TZ)
        block_map = {
            "sec": {
                "data": {
                    "type": "heading1",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "近 7 日更新日志"}}},
                }
            },
            "h1": {
                "data": {
                    "type": "heading3",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "2 月 20 日"}}},
                }
            },
            "b1": {
                "data": {
                    "type": "bullet",
                    "parent_id": "h1",
                    "text": {"initialAttributedTexts": {"text": {"0": "《 》 OpenClaw 新教程"}}},
                }
            },
            "h2": {
                "data": {
                    "type": "heading3",
                    "parent_id": "other-root",
                    "text": {"initialAttributedTexts": {"text": {"0": "2 月 20 日"}}},
                }
            },
            "b2": {
                "data": {
                    "type": "bullet",
                    "parent_id": "h2",
                    "text": {"initialAttributedTexts": {"text": {"0": "不会被收集"}}},
                }
            },
        }
        out = extract_waytoagi_recent_updates_from_block_map(block_map, now, "https://example.com")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["date"], "2026-02-20")
        self.assertEqual(out[0]["title"], "OpenClaw 新教程")

    def test_extract_recent_updates_with_mention_url_match(self):
        now = datetime(2026, 2, 20, 10, 0, tzinfo=SH_TZ)
        block_map = {
            "sec": {
                "data": {
                    "type": "heading1",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "近 7 日更新日志"}}},
                }
            },
            "h1": {
                "data": {
                    "type": "heading3",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "2 月 20 日"}}},
                }
            },
            "b1": {
                "data": {
                    "type": "bullet",
                    "parent_id": "h1",
                    "text": {"initialAttributedTexts": {"text": {"0": "OpenClaw 新教程"}}},
                }
            },
        }
        mention_urls = {"OpenClaw 新教程": "https://waytoagi.feishu.cn/wiki/abc123"}
        out = extract_waytoagi_recent_updates_from_block_map(
            block_map, now, "https://example.com", mention_urls
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["url"], "https://waytoagi.feishu.cn/wiki/abc123")

    def test_extract_recent_updates_fallback_to_page_url(self):
        now = datetime(2026, 2, 20, 10, 0, tzinfo=SH_TZ)
        block_map = {
            "sec": {
                "data": {
                    "type": "heading1",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "近 7 日更新日志"}}},
                }
            },
            "h1": {
                "data": {
                    "type": "heading3",
                    "parent_id": "root",
                    "text": {"initialAttributedTexts": {"text": {"0": "2 月 20 日"}}},
                }
            },
            "b1": {
                "data": {
                    "type": "bullet",
                    "parent_id": "h1",
                    "text": {"initialAttributedTexts": {"text": {"0": "No Match Title"}}},
                }
            },
        }
        mention_urls = {"Some Other Title": "https://waytoagi.feishu.cn/wiki/abc123"}
        out = extract_waytoagi_recent_updates_from_block_map(
            block_map, now, "https://example.com/parent", mention_urls
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["url"], "https://example.com/parent")

    def test_block_text_and_link_extracts_text(self):
        block_data = {
            "text": {
                "initialAttributedTexts": {
                    "text": {
                        "0": {"text": "Hello "},
                        "1": {"text": "World"},
                    }
                }
            }
        }
        text, link = block_text_and_link(block_data)
        self.assertEqual(text, "Hello World")
        self.assertEqual(link, "")

    def test_block_text_and_link_extracts_apool_mention_doc(self):
        block_data = {
            "text": {
                "apool": {
                    "numToAttrib": {
                        "0": ["author", "user1"],
                        "1": [
                            "inline-component",
                            '{"id":"abc","type":"mention_doc","data":{"raw_url":"https://waytoagi.feishu.cn/wiki/doc123","title":"Test Doc"}}',
                        ],
                    }
                },
                "initialAttributedTexts": {
                    "text": {
                        "0": "《 》This is a summary description",
                    }
                },
            }
        }
        text, link = block_text_and_link(block_data)
        self.assertEqual(text, "《 》This is a summary description")
        self.assertEqual(link, "https://waytoagi.feishu.cn/wiki/doc123")

    def test_block_text_and_link_apool_with_double_escape(self):
        block_data = {
            "text": {
                "apool": {
                    "numToAttrib": {
                        "1": [
                            "inline-component",
                            '{\\"id\\":\\"abc\\",\\"type\\":\\"mention_doc\\",\\"data\\":{\\"raw_url\\":\\"https://test.com/1\\"}}',
                        ],
                    }
                },
                "initialAttributedTexts": {
                    "text": {"0": "Summary text"},
                },
            }
        }
        text, link = block_text_and_link(block_data)
        self.assertEqual(text, "Summary text")
        self.assertEqual(link, "https://test.com/1")

    def test_extract_all_mention_doc_urls(self):
        html = r'{"id":"x","type":"mention_doc","data":{"title":"历史更新","raw_url":"https://example.com/1"}}'
        html += r'{"id":"y","type":"mention_doc","data":{"title":"OpenClaw教程","raw_url":"https://example.com/2"}}'
        result = extract_all_mention_doc_urls(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result["历史更新"], "https://example.com/1")
        self.assertEqual(result["OpenClaw教程"], "https://example.com/2")

    def test_extract_all_mention_doc_urls_single_escape(self):
        html = '{"id":"x","type":"mention_doc","data":{"title":"Test Doc","raw_url":"https://test.com/1"}}'
        result = extract_all_mention_doc_urls(html)
        self.assertEqual(result["Test Doc"], "https://test.com/1")

    def test_extract_all_mention_doc_urls_skips_empty(self):
        html = r'{"id":"x","type":"mention_doc","data":{"title":"","raw_url":""}}'
        result = extract_all_mention_doc_urls(html)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
