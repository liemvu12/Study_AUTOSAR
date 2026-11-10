# YouTube Compliance Risk Matrix & Evaluation Rubric

This rubric establishes objective criteria for assessing the compliance, monetization, and copyright risk profiles of YouTube channels and automated video workflows.

---

## 1. Multi-Dimensional Risk Evaluation Matrix

| Risk Dimension | LOW RISK (Compliant) | MEDIUM RISK (Monitor/Disclose) | HIGH RISK (Danger of Rejection) | CRITICAL RISK (Immediate Violation) |
| :--- | :--- | :--- | :--- | :--- |
| **Script & Content Originality** | 100% human-written or human-edited script with unique arguments, empirical data, or personal storytelling. | AI-generated first draft heavily revised, fact-checked, and restructured by a human editor. | Raw LLM output read verbatim without source verification, fact-checking, or stylistic editing. | Scraped articles, Wikipedia pages, or Reddit threads passed directly to text-to-speech with no changes. |
| **Voiceover & Audio** | Human voiceover or licensed ultra-realistic AI voice with human cadence and intonation editing. | High-quality AI voice reading a custom, original script clearly identified with educational intent. | Monotonous robotic TTS reading generic content. Viewer cannot distinguish voice from standard bot narrations. | AI voice cloning of real persons, celebrities, or politicians without express legal authorization. |
| **Visual Assets & B-Roll** | Original footage, custom animations, or paid commercial stock assets with custom motion graphics. | Generative AI images/video combined with public domain footage and on-screen graphical annotations. | Unaltered third-party clips downloaded from YouTube/TikTok/X compiled into a montage with minimal overlay. | Copyrighted movie scenes, TV broadcasts, or music videos used without licenses under false claims of "Fair Use". |
| **AI Disclosure** | No realistic synthetic depiction of real events/people; AI used for background/illustration only. | Realistic AI elements present and explicitly disclosed via YouTube Creator Studio synthetic media toggle. | Realistic AI scenes depicting fake incidents, disasters, or medical claims without disclosure. | Synthetic media impersonating public figures, fabricating defamatory news, or generating non-consensual imagery. |
| **Audience Demographics & COPPA** | Explicit adult/general audience content with zero child-appealing tropes or themes. | Family-friendly content with mixed appeal; properly evaluated and confirmed as "Not Made for Kids" under FTC test. | Content ambiguously directed at young children (e.g., Nursery rhymes, toy unboxings) tagged as "Not Made for Kids". | Intentional false tagging of child-directed content to preserve personalized ad revenue. |
| **Advertiser Friendliness** | Neutral, professional educational tone. Zero profanity in first 7s, advertiser-friendly topics. | Occasional mild profanity or discussion of historic conflicts in strictly educational context. | Sensationalized tragedy exploitation, conspiracy theories, graphic imagery, or repeated profanity. | Hate speech, promotion of illegal goods, self-harm, medical misinformation, or extremist rhetoric. |
| **Platform Terms of Service** | Data collected via official YouTube Data API v3 within official project quota allocations. | Manual data collection or platform-provided analytics export through YouTube Studio. | High-concurrency automated scrapers generating bulk requests against YouTube frontend endpoints. | Account sharing, botting views/subscribers, automated bulk uploading of thousands of generated shorts. |

---

## 2. Actionable Decision Gates

### Gate 1: YPP Application Readiness
* If a channel exhibits **more than one HIGH RISK** dimension:
  $$\text{Verdict} = \mathbf{REJECT\ PRE\text{-}SUBMISSION}$$
  *Action:* The creator must replace automated layers with human editorial value before submitting for human reviewer audit.

### Gate 2: Synthetic Media Tagging
* If video contains realistic simulations of people, locations, or historical occurrences:
  $$\text{Action} = \mathbf{MANDATORY\ STUDIO\ CHECKBOX\ ACTIVATION}$$
  *Risk Prevention:* Prevents algorithmic demonetization or strike under YouTube Synthetic Media Policy (Answer 14328491).

### Gate 3: Copyright & Content ID Defense
* All background music and sound effects must come from:
  1. YouTube Audio Library (100% safe, pre-cleared).
  2. Commercial sync-licensed platforms (Epidemic Sound, Artlist) with channel whitelisting active.
  3. Original royalty-free compositions with verifiable commercial transfer certificates.
