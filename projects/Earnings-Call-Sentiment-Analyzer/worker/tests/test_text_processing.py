import unittest

from app.text_processing import parse_transcript


class TextProcessingTest(unittest.TestCase):
    def test_detects_sections_speakers_roles_and_chunks(self):
        transcript = """
        PREPARED REMARKS
        Alex Morgan - Chief Executive Officer:
        We delivered strong growth. Customers expanded their use of the platform.

        FINANCIAL RESULTS
        Jamie Lee - Chief Financial Officer:
        Revenue increased 15 percent. Margins were stable.

        QUESTION AND ANSWER SESSION
        Taylor Reed - Equity Research Analyst:
        Can you discuss the weaker bookings trend?
        """

        chunks = parse_transcript(transcript)

        self.assertEqual(3, len(chunks))
        self.assertEqual("PREPARED_REMARKS", chunks[0].section_name)
        self.assertEqual("CEO", chunks[0].speaker_role)
        self.assertEqual("FINANCIAL_RESULTS", chunks[1].section_name)
        self.assertEqual("CFO", chunks[1].speaker_role)
        self.assertEqual("Q_AND_A", chunks[2].section_name)
        self.assertEqual("ANALYST", chunks[2].speaker_role)

    def test_groups_no_more_than_three_sentences(self):
        transcript = "PREPARED REMARKS\nOne is good. Two is fine. Three is steady. Four is difficult."
        chunks = parse_transcript(transcript)
        self.assertEqual(2, len(chunks))

    def test_short_sentences_that_mention_outlook_are_not_dropped_as_headings(self):
        transcript = """
        PREPARED REMARKS
        Alex Morgan - Chief Executive Officer:
        Our outlook is strong.

        GUIDANCE AND OUTLOOK
        We expect steady growth.
        """

        chunks = parse_transcript(transcript)

        self.assertEqual(2, len(chunks))
        self.assertEqual("PREPARED_REMARKS", chunks[0].section_name)
        self.assertEqual("Our outlook is strong.", chunks[0].chunk_text)
        self.assertEqual("GUIDANCE", chunks[1].section_name)

    def test_parses_timestamped_vendor_transcript_turns(self):
        transcript = """
        PRESENTATION
        Operator
        00:00:00
        Welcome to the call.

        John Smith
        President and CEO at Example Corp
        00:01:00
        We delivered strong results.

        Operator
        00:10:00
        We will now begin the question-and-answer session.

        Jane Doe
        Analyst at Example Bank
        00:10:20
        What is your outlook?
        PARTICIPANTS
        """

        chunks = parse_transcript(transcript)

        self.assertTrue(all(chunk.speaker_name for chunk in chunks))
        self.assertEqual({"PREPARED_REMARKS", "Q_AND_A"}, {chunk.section_name for chunk in chunks})
        self.assertIn("CEO", {chunk.speaker_role for chunk in chunks})
        self.assertIn("ANALYST", {chunk.speaker_role for chunk in chunks})

    def test_parses_speaker_and_timestamp_on_the_same_line(self):
        transcript = """
        PRESENTATION
        Operator 00:00:00
        Welcome to the call.
        Celeste Mastin 00:02:00
        President and CEO at Example Corp
        We delivered strong results. Operator, please open the line for questions.
        Operator 00:28:33
        Your first question comes from Ghansham Panjabi with Baird.
        Ghansham Panjabi 00:28:55
        Analyst at Baird
        Can you discuss the outlook?
        PARTICIPANTS
        """

        chunks = parse_transcript(transcript)
        roles_by_speaker = {chunk.speaker_name: chunk.speaker_role for chunk in chunks}

        self.assertTrue(all(chunk.speaker_name for chunk in chunks))
        self.assertEqual("CEO", roles_by_speaker["Celeste Mastin"])
        self.assertEqual("ANALYST", roles_by_speaker["Ghansham Panjabi"])
        self.assertEqual("Q_AND_A", chunks[-1].section_name)

    def test_uses_pdf_participant_roster_and_intro_to_infer_roles(self):
        transcript = """
        Participants
        Jeremy Steffan executive
        Donald Nolan executive
        Mark Augdahl executive
        Julio Romero analyst
        Call transcript
        Operator
        Welcome to the call.
        Jeremy Steffan
        On the call today are Don Nolan, our Chief Executive Officer, and Mark Augdahl, our Chief Financial Officer.
        Donald Nolan
        We made good progress this quarter.
        Mark Augdahl
        Revenue was stable. We will now open the call to questions.
        Operator
        Our first question comes from Julio Romero.
        Julio Romero
        Can you discuss pricing?
        """

        chunks = parse_transcript(transcript)
        roles_by_speaker = {chunk.speaker_name: chunk.speaker_role for chunk in chunks}

        self.assertTrue(all(chunk.speaker_name for chunk in chunks))
        self.assertEqual("CEO", roles_by_speaker["Donald Nolan"])
        self.assertEqual("CFO", roles_by_speaker["Mark Augdahl"])
        self.assertEqual("ANALYST", roles_by_speaker["Julio Romero"])
        self.assertEqual("Q_AND_A", chunks[-1].section_name)

    def test_resolves_unknown_analyst_from_operator_announcement(self):
        transcript = """
        Call transcript
        Operator
        We will now begin the question-and-answer session. Our next question comes from Josh user with Singular Research.
        Unknown Analyst
        Can you discuss demand?
        """

        chunks = parse_transcript(transcript)
        analyst_chunk = chunks[-1]

        self.assertEqual("Josh User", analyst_chunk.speaker_name)
        self.assertEqual("ANALYST", analyst_chunk.speaker_role)
        self.assertEqual("Q_AND_A", analyst_chunk.section_name)


if __name__ == "__main__":
    unittest.main()
