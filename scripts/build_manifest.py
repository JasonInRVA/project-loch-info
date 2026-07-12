import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
MANIFEST_JSON = DOCS_DIR / "manifest.json"
MANIFEST_CSV = DOCS_DIR / "manifest.csv"

USACE_NOTICE_URL = "https://www.nao.usace.army.mil/Media/Public-Notices/Article/4484789/nao-2026-00182-vmrc-project-loch-chesterfield-county-virginia-wauford-prm-site/"
VMRC_DOCKET_URL = "https://webapps.mrc.virginia.gov/public/habitat/additionaldocs.php?id=20260171"
CHESTERFIELD_CIVICCLERK_URL = "https://chesterfieldcova.portal.civicclerk.com/"

SUMMARY_PATHS = {
    "docs/chesterfield/2025-06-25_Aeris_Investments_Fixed_Tax_Rate_Agreement.pdf": "summaries/aeris-tax-agreement.html",
    "docs/chesterfield/2025-06-25_Chesterfield_BOS_Agenda_Packet.pdf": "summaries/chesterfield-bos-agenda-packet.html",
    "docs/chesterfield/2025-06-25_Chesterfield_BOS_Minutes_Project_Loch_Approval.pdf": "summaries/chesterfield-bos-minutes-project-loch-approval.html",
    "docs/chesterfield/2025-08-27_Chesterfield_BOS_Minutes_Project_Loch_Google_Identity.pdf": "summaries/bos-minutes-google-identity.html",
    "docs/chesterfield/2026-03-19_Chesterfield_EDA_Minutes_Bermuda_Hundred_and_Upper_Magnolia_Update.pdf": "summaries/chesterfield-eda-minutes-march-2026.html",
    "docs/chesterfield/2026-04-16_Chesterfield_EDA_Minutes_Upper_Magnolia_Update.pdf": "summaries/chesterfield-eda-minutes-april-2026.html",
    "docs/chesterfield/2026-05-21_Chesterfield_EDA_Minutes_Google_Infrastructure_Grant.pdf": "summaries/chesterfield-eda-infrastructure-grant.html",
    "docs/chesterfield/2026-05-27_Chesterfield_Presentation_Project_Loch_and_Skye_Google_Transactions.pdf": "summaries/chesterfield-presentation-google-transactions.html",
    "docs/deq/2026-02-18_DEQ_Additional_Information_Request_1.pdf": "summaries/deq-additional-info-request-1.html",
    "docs/deq/2026-03-31_DEQ_Additional_Information_Request_2.pdf": "summaries/deq-additional-info-request-2.html",
    "docs/deq/2026-06-18_DEQ_Additional_Information_Request_4.pdf": "summaries/deq-additional-info-request-4.html",
    "docs/deq/2026-07-08_DEQ_Request_to_Confirm_Wauford_SSWD_Withdrawal.pdf": "summaries/deq-request-confirm-withdrawal.html",
    "docs/google/2026-01-29_Project_Loch_DoD_SAFE_Transmittal_and_Supporting_Files.pdf": "summaries/dod-safe-transmittal.html",
    "docs/google/2026-01-29_Project_Loch_Environmental_Report_and_Technical_Appendices.pdf": "summaries/environmental-report.html",
    "docs/google/2026-01-29_Project_Loch_Joint_Permit_Application_Package.pdf": "summaries/joint-permit-application.html",
    "docs/google/2026-07-02_Google_Response_to_DEQ_Additional_Information_Request_4.pdf": "summaries/google-response-request-4.html",
    "docs/google/2026-07-08_Google_Confirmation_of_Wauford_SSWD_Withdrawal.pdf": "summaries/google-confirmation-withdrawal.html",
    "docs/usace/2026-05-13_USACE_NAO-2026-00182_Attachments.pdf": "summaries/usace-attachments.html",
    "docs/vmrc/2026-04-29_VMRC_Non-Jurisdiction_Letter.pdf": "summaries/vmrc-non-jurisdiction-letter.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_267375.pdf": "summaries/vmrc-docket-part-1.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_267376.pdf": "summaries/vmrc-docket-part-2.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_267377.pdf": "summaries/vmrc-docket-part-3.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_268539.pdf": "summaries/vmrc-docket-deq-request-1.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_273493.pdf": "summaries/vmrc-docket-deq-request-2.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_278930.pdf": "summaries/vmrc-docket-non-jurisdiction.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_285027.pdf": "summaries/vmrc-docket-deq-request-4.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_286788.pdf": "summaries/vmrc-docket-applicant-response-4.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_287616.pdf": "summaries/vmrc-docket-deq-confirmation-request.html",
    "docs/vmrc/VMRC_JPA-26-0171_Document_287625.pdf": "summaries/vmrc-docket-applicant-confirmation-withdrawal.html",
}


MANUAL_METADATA = {
    "docs/chesterfield/2025-06-25_Aeris_Investments_Fixed_Tax_Rate_Agreement.pdf": {
        "date": "2025-06-25",
        "title": "Aeris Investments Fixed Tax Rate Agreement",
        "agency": "Chesterfield County Board of Supervisors",
        "originator": "Chesterfield County and Aeris Investments LLC",
        "description": "County agreement document for Project Loch, identified in the text as a proposed large-scale data center project on approximately 342 acres in Chesterfield County.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1232/files/attachment/11740",
        "status": "historical",
        "record_type": "established fact",
        "series": "County tax agreement record",
        "series_order": 2,
        "summary_path": "summaries/aeris-tax-agreement.html",
        "canonical_archived_path": "docs/chesterfield/2025-06-25_Aeris_Investments_Fixed_Tax_Rate_Agreement.pdf",
    },
    "docs/chesterfield/2025-06-25_Chesterfield_BOS_Agenda_Packet.pdf": {
        "date": "2025-06-25",
        "title": "Chesterfield Board of Supervisors Agenda Packet",
        "agency": "Chesterfield County Board of Supervisors",
        "originator": "Chesterfield County Board of Supervisors",
        "description": "Agenda packet for the June 25, 2025 Board of Supervisors meeting, including the county item titled 'Approval of a Fixed Tax Rate Agreement with Project Loch (Aeris).'",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1232/files/agenda/3602",
        "status": "historical",
        "record_type": "established fact",
        "series": "County board meeting record",
        "series_order": 1,
        "canonical_archived_path": "docs/chesterfield/2025-06-25_Chesterfield_BOS_Agenda_Packet.pdf",
    },
    "docs/chesterfield/2025-06-25_Chesterfield_BOS_Minutes_Project_Loch_Approval.pdf": {
        "date": "2025-06-25",
        "title": "Chesterfield Board of Supervisors Minutes on Project Loch Approval",
        "agency": "Chesterfield County Board of Supervisors",
        "originator": "Chesterfield County Board of Supervisors",
        "description": "Board minutes recording formal approval of the fixed tax rate agreement with Project Loch (Aeris), including the statement that the agreement matched the one approved for Project Skye.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1232/files/agenda/3618",
        "status": "historical",
        "record_type": "established fact",
        "series": "County board meeting record",
        "series_order": 3,
        "summary_path": "summaries/chesterfield-bos-minutes-project-loch-approval.html",
        "canonical_archived_path": "docs/chesterfield/2025-06-25_Chesterfield_BOS_Minutes_Project_Loch_Approval.pdf",
    },
    "docs/chesterfield/2025-08-27_Chesterfield_BOS_Minutes_Project_Loch_Google_Identity.pdf": {
        "date": "2025-08-27",
        "title": "Chesterfield Board of Supervisors Minutes on Google Identity",
        "agency": "Chesterfield County Board of Supervisors",
        "originator": "Chesterfield County Board of Supervisors",
        "description": "Board minutes recording the public statement that Project Peanut, Project Loch (Aeris), and Project Skye (Skyward) were Google projects.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1234/files/agenda/3658",
        "status": "historical",
        "record_type": "established fact",
        "series": "County board meeting record",
        "series_order": 2,
        "summary_path": "summaries/bos-minutes-google-identity.html",
        "canonical_archived_path": "docs/chesterfield/2025-08-27_Chesterfield_BOS_Minutes_Project_Loch_Google_Identity.pdf",
    },
    "docs/chesterfield/2026-03-19_Chesterfield_EDA_Minutes_Bermuda_Hundred_and_Upper_Magnolia_Update.pdf": {
        "date": "2026-03-19",
        "title": "Chesterfield EDA Minutes on Bermuda Hundred and Upper Magnolia Updates",
        "agency": "Chesterfield County Economic Development Authority",
        "originator": "Chesterfield County Economic Development Authority",
        "description": "EDA meeting minutes stating that Google's Bermuda Hundred data center site was actively undergoing grading and that the first building was anticipated to be operational in the fourth quarter of 2027, while also outlining permit and infrastructure progress at Upper Magnolia Green.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1917/files/agenda/4000",
        "status": "historical",
        "record_type": "established fact",
        "series": "County project status record",
        "series_order": 1,
        "summary_path": "summaries/chesterfield-eda-minutes-march-2026.html",
        "canonical_archived_path": "docs/chesterfield/2026-03-19_Chesterfield_EDA_Minutes_Bermuda_Hundred_and_Upper_Magnolia_Update.pdf",
    },
    "docs/chesterfield/2026-04-16_Chesterfield_EDA_Minutes_Upper_Magnolia_Update.pdf": {
        "date": "2026-04-16",
        "title": "Chesterfield EDA Minutes on Upper Magnolia Update",
        "agency": "Chesterfield County Economic Development Authority",
        "originator": "Chesterfield County Economic Development Authority",
        "description": "EDA meeting minutes reporting continued infrastructure progress at Upper Magnolia Green and a planned community update meeting, while noting no change in Meadowville project-status reporting from the prior month.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1918/files/agenda/4095",
        "status": "historical",
        "record_type": "established fact",
        "series": "County project status record",
        "series_order": 2,
        "summary_path": "summaries/chesterfield-eda-minutes-april-2026.html",
        "canonical_archived_path": "docs/chesterfield/2026-04-16_Chesterfield_EDA_Minutes_Upper_Magnolia_Update.pdf",
    },
    "docs/chesterfield/2026-05-21_Chesterfield_EDA_Minutes_Google_Infrastructure_Grant.pdf": {
        "date": "2026-05-21",
        "title": "Chesterfield EDA Minutes on Google Infrastructure Grant",
        "agency": "Chesterfield County Economic Development Authority",
        "originator": "Chesterfield County Economic Development Authority",
        "description": "EDA meeting minutes stating that a $25 million grant funded engineering and design of water, sewer, and roadway infrastructure serving the Google campus and an adjacent pad-ready development site.",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/1919/files/agenda/4130",
        "status": "historical",
        "record_type": "established fact",
        "series": "County infrastructure record",
        "series_order": 1,
        "canonical_archived_path": "docs/chesterfield/2026-05-21_Chesterfield_EDA_Minutes_Google_Infrastructure_Grant.pdf",
    },
    "docs/chesterfield/2026-05-27_Chesterfield_Presentation_Project_Loch_and_Skye_Google_Transactions.pdf": {
        "date": "2026-05-27",
        "title": "Chesterfield Presentation on Project Loch and Skye Google Transactions",
        "agency": "Chesterfield County Board of Supervisors",
        "originator": "Chesterfield County",
        "description": "County presentation file whose text includes 'Project Loch & Skye Google Transactions' and 'Google Land Transactions.'",
        "official_source_url": "https://chesterfieldcova.portal.civicclerk.com/event/2026/files/attachment/14942",
        "status": "historical",
        "record_type": "established fact",
        "series": "County land transaction record",
        "series_order": 1,
        "canonical_archived_path": "docs/chesterfield/2026-05-27_Chesterfield_Presentation_Project_Loch_and_Skye_Google_Transactions.pdf",
    },
    "docs/deq/2026-02-18_DEQ_Additional_Information_Request_1.pdf": {
        "date": "2026-02-18",
        "title": "DEQ Additional Information Request 1",
        "agency": "Virginia DEQ",
        "originator": "Virginia Department of Environmental Quality",
        "description": "Agency letter requesting additional information and a single-and-complete worksheet for Joint Permit Application 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=268539",
        "status": "historical",
        "record_type": "agency comment",
        "series": "DEQ additional information requests",
        "series_order": 1,
        "summary_path": "summaries/deq-additional-info-request-1.html",
        "canonical_archived_path": "docs/deq/2026-02-18_DEQ_Additional_Information_Request_1.pdf",
    },
    "docs/deq/2026-03-31_DEQ_Additional_Information_Request_2.pdf": {
        "date": "2026-03-31",
        "title": "DEQ Additional Information Request 2",
        "agency": "Virginia DEQ",
        "originator": "Virginia Department of Environmental Quality",
        "description": "Agency follow-up stating that outstanding items remained after the applicant's March 16 response materials.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=273493",
        "status": "historical",
        "record_type": "agency comment",
        "series": "DEQ additional information requests",
        "series_order": 2,
        "canonical_archived_path": "docs/deq/2026-03-31_DEQ_Additional_Information_Request_2.pdf",
    },
    "docs/deq/2026-06-18_DEQ_Additional_Information_Request_4.pdf": {
        "date": "2026-06-18",
        "title": "DEQ Additional Information Request 4",
        "agency": "Virginia DEQ",
        "originator": "Virginia Department of Environmental Quality",
        "description": "Agency request for more information after review of response materials received June 3, 2026, including questions about compensatory-mitigation approach rather than relocation of the Chesterfield project site.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=285027",
        "status": "historical",
        "record_type": "agency comment",
        "series": "DEQ additional information requests",
        "series_order": 4,
        "summary_path": "summaries/deq-additional-info-request-4.html",
        "canonical_archived_path": "docs/deq/2026-06-18_DEQ_Additional_Information_Request_4.pdf",
    },
    "docs/deq/2026-07-08_DEQ_Request_to_Confirm_Wauford_SSWD_Withdrawal.pdf": {
        "date": "2026-07-08",
        "title": "DEQ Request to Confirm Wauford SSWD Withdrawal",
        "agency": "Virginia DEQ",
        "originator": "Virginia Department of Environmental Quality",
        "description": "Agency email asking whether the applicant was withdrawing the SSWD associated with the originally proposed Wauford permittee-responsible mitigation site, which was a separate compensatory-mitigation proposal and not the main Chesterfield project location.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=287616",
        "status": "current",
        "record_type": "agency comment",
        "series": "Wauford mitigation withdrawal correspondence",
        "series_order": 1,
        "summary_path": "summaries/deq-request-confirm-withdrawal.html",
        "canonical_archived_path": "docs/deq/2026-07-08_DEQ_Request_to_Confirm_Wauford_SSWD_Withdrawal.pdf",
    },
    "docs/google/2026-01-29_Project_Loch_DoD_SAFE_Transmittal_and_Supporting_Files.pdf": {
        "date": "2026-01-29",
        "title": "Project Loch DoD SAFE Transmittal and Supporting Files",
        "agency": "Google / Timmons Group",
        "originator": "Google, LLC and Timmons Group",
        "description": "Applicant transmittal record for the initial application package. The archived PDF preserves a historical transfer notice, but the public site does not expose its expired file-transfer credentials.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267375",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "Initial application package",
        "series_order": 1,
        "sensitive_source_handling": "Official source link points to the VMRC docket copy instead of the expired transfer link preserved in the document.",
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_DoD_SAFE_Transmittal_and_Supporting_Files.pdf",
    },
    "docs/google/2026-01-29_Project_Loch_Environmental_Report_and_Technical_Appendices.pdf": {
        "date": "2026-01-29",
        "title": "Project Loch Environmental Report and Technical Appendices",
        "agency": "Google / Timmons Group",
        "originator": "Google, LLC and Timmons Group",
        "description": "Applicant environmental report volume containing technical appendices and supporting wetland-impact documentation submitted with the initial application package.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267377",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "Initial application package",
        "series_order": 3,
        "summary_path": "summaries/environmental-report.html",
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_Environmental_Report_and_Technical_Appendices.pdf",
    },
    "docs/google/2026-01-29_Project_Loch_Joint_Permit_Application_Package.pdf": {
        "date": "2026-01-29",
        "title": "Project Loch Joint Permit Application Package",
        "agency": "Google / Timmons Group",
        "originator": "Google, LLC and Timmons Group",
        "description": "Applicant's main joint permit application volume for the proposed Project Loch campus, including narrative, drawings, and permit-request materials.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267376",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "Initial application package",
        "series_order": 2,
        "summary_path": "summaries/joint-permit-application.html",
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_Joint_Permit_Application_Package.pdf",
    },
    "docs/google/2026-07-02_Google_Response_to_DEQ_Additional_Information_Request_4.pdf": {
        "date": "2026-07-02",
        "title": "Google Response to DEQ Additional Information Request 4",
        "agency": "Google / Timmons Group",
        "originator": "Google, LLC and Timmons Group",
        "description": "Applicant response package transmitted to DEQ in response to the June 18 additional information request.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=286788",
        "status": "current",
        "record_type": "applicant assertion",
        "series": "Responses to DEQ request 4",
        "series_order": 1,
        "summary_path": "summaries/google-response-request-4.html",
        "canonical_archived_path": "docs/google/2026-07-02_Google_Response_to_DEQ_Additional_Information_Request_4.pdf",
    },
    "docs/google/2026-07-08_Google_Confirmation_of_Wauford_SSWD_Withdrawal.pdf": {
        "date": "2026-07-08",
        "title": "Google Confirmation of Wauford SSWD Withdrawal",
        "agency": "Google / Timmons Group",
        "originator": "Google, LLC and Timmons Group",
        "description": "Applicant email confirming withdrawal of the SSWD associated with the originally proposed Wauford mitigation site, which functioned as a separate compensatory-mitigation proposal rather than the main project location.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=287625",
        "status": "current",
        "record_type": "applicant assertion",
        "series": "Wauford mitigation withdrawal correspondence",
        "series_order": 2,
        "summary_path": "summaries/google-confirmation-withdrawal.html",
        "canonical_archived_path": "docs/google/2026-07-08_Google_Confirmation_of_Wauford_SSWD_Withdrawal.pdf",
    },
    "docs/usace/2026-05-13_USACE_NAO-2026-00182_Attachments.pdf": {
        "date": "2026-05-13",
        "title": "USACE NAO-2026-00182 Attachments",
        "agency": "USACE Norfolk District",
        "originator": "U.S. Army Corps of Engineers, Norfolk District",
        "description": "Attachment package linked from the federal public notice, including maps, plans, and supporting figures associated with the Section 404 review.",
        "official_source_url": USACE_NOTICE_URL,
        "status": "historical",
        "record_type": "established fact",
        "series": "Federal public notice record",
        "series_order": 2,
        "official_source_note": "Official source is the USACE public notice page that links to the attachment package.",
        "canonical_archived_path": "docs/usace/2026-05-13_USACE_NAO-2026-00182_Attachments.pdf",
    },
    "docs/vmrc/2026-04-29_VMRC_Non-Jurisdiction_Letter.pdf": {
        "date": "2026-04-29",
        "title": "VMRC Non-Jurisdiction Letter",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission",
        "description": "VMRC email stating that the proposal did not fall within VMRC jurisdiction and that no authorization from that agency would be required.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=278930",
        "status": "historical",
        "record_type": "established fact",
        "series": "VMRC jurisdiction determination",
        "series_order": 1,
        "summary_path": "summaries/vmrc-non-jurisdiction-letter.html",
        "canonical_archived_path": "docs/vmrc/2026-04-29_VMRC_Non-Jurisdiction_Letter.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_267375.pdf": {
        "date": "2026-02-03",
        "title": "VMRC Docket Copy: 2026-0171 Part 1",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the applicant's initial transmittal and supporting files for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267375",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "VMRC docket copies",
        "series_order": 1,
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_DoD_SAFE_Transmittal_and_Supporting_Files.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_267376.pdf": {
        "date": "2026-02-03",
        "title": "VMRC Docket Copy: 2026-0171 Part 2",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the main joint permit application package for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267376",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "VMRC docket copies",
        "series_order": 2,
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_Joint_Permit_Application_Package.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_267377.pdf": {
        "date": "2026-02-03",
        "title": "VMRC Docket Copy: 2026-0171 Part 3",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the environmental report and technical appendices for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=267377",
        "status": "historical",
        "record_type": "applicant assertion",
        "series": "VMRC docket copies",
        "series_order": 3,
        "canonical_archived_path": "docs/google/2026-01-29_Project_Loch_Environmental_Report_and_Technical_Appendices.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_268539.pdf": {
        "date": "2026-02-19",
        "title": "VMRC Docket Copy: DEQ Additional Information Request 1",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of DEQ's first additional information request for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=268539",
        "status": "historical",
        "record_type": "agency comment",
        "series": "VMRC docket copies",
        "series_order": 4,
        "canonical_archived_path": "docs/deq/2026-02-18_DEQ_Additional_Information_Request_1.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_273493.pdf": {
        "date": "2026-04-01",
        "title": "VMRC Docket Copy: DEQ Additional Information Request 2",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of DEQ's second additional information request for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=273493",
        "status": "historical",
        "record_type": "agency comment",
        "series": "VMRC docket copies",
        "series_order": 5,
        "canonical_archived_path": "docs/deq/2026-03-31_DEQ_Additional_Information_Request_2.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_278930.pdf": {
        "date": "2026-04-29",
        "title": "VMRC Docket Copy: Non-Jurisdiction Letter",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the non-jurisdiction letter for JPA 26-0171.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=278930",
        "status": "historical",
        "record_type": "established fact",
        "series": "VMRC docket copies",
        "series_order": 6,
        "canonical_archived_path": "docs/vmrc/2026-04-29_VMRC_Non-Jurisdiction_Letter.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_285027.pdf": {
        "date": "2026-06-22",
        "title": "VMRC Docket Copy: DEQ Additional Information Request 4",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of DEQ's fourth additional information request for JPA 26-0171, including compensatory-mitigation questions tied to a separate proposed mitigation site.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=285027",
        "status": "historical",
        "record_type": "agency comment",
        "series": "VMRC docket copies",
        "series_order": 7,
        "canonical_archived_path": "docs/deq/2026-06-18_DEQ_Additional_Information_Request_4.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_286788.pdf": {
        "date": "2026-07-02",
        "title": "VMRC Docket Copy: Applicant Response to DEQ Request 4",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the applicant's July 2 response package to DEQ's fourth additional information request.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=286788",
        "status": "current",
        "record_type": "applicant assertion",
        "series": "VMRC docket copies",
        "series_order": 8,
        "canonical_archived_path": "docs/google/2026-07-02_Google_Response_to_DEQ_Additional_Information_Request_4.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_287616.pdf": {
        "date": "2026-07-09",
        "title": "VMRC Docket Copy: DEQ Wauford Withdrawal Confirmation Request",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of DEQ's July 8 email asking the applicant to confirm withdrawal of the Wauford SSWD for a separate compensatory-mitigation site.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=287616",
        "status": "current",
        "record_type": "agency comment",
        "series": "VMRC docket copies",
        "series_order": 9,
        "canonical_archived_path": "docs/deq/2026-07-08_DEQ_Request_to_Confirm_Wauford_SSWD_Withdrawal.pdf",
    },
    "docs/vmrc/VMRC_JPA-26-0171_Document_287625.pdf": {
        "date": "2026-07-09",
        "title": "VMRC Docket Copy: Applicant Confirmation of Wauford Withdrawal",
        "agency": "Virginia Marine Resources Commission",
        "originator": "Virginia Marine Resources Commission docket copy",
        "description": "VMRC-posted docket copy of the applicant's July 8 confirmation that the Wauford SSWD for a separate compensatory-mitigation site should be withdrawn.",
        "official_source_url": "https://webapps.mrc.virginia.gov/public/habitat/getADD.php?id=287625",
        "status": "current",
        "record_type": "applicant assertion",
        "series": "VMRC docket copies",
        "series_order": 10,
        "canonical_archived_path": "docs/google/2026-07-08_Google_Confirmation_of_Wauford_SSWD_Withdrawal.pdf",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_count(path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"No page count found for {path}")


def file_size(path: Path) -> int:
    return path.stat().st_size


def sort_key(record: dict) -> tuple:
    return (record["date"], record["title"], record["archived_path"])


def build_records() -> list[dict]:
    pdf_paths = sorted(DOCS_DIR.glob("**/*.pdf"))
    records = []

    for pdf_path in pdf_paths:
        relative_path = pdf_path.relative_to(ROOT).as_posix()
        metadata = MANUAL_METADATA.get(relative_path)
        if metadata is None:
            raise KeyError(f"Missing manual metadata for {relative_path}")

        summary_path = SUMMARY_PATHS.get(relative_path) or metadata.get("summary_path")
        if summary_path:
            metadata = {**metadata, "summary_path": summary_path}

        record = {
            **metadata,
            "year": metadata["date"][:4],
            "archived_path": relative_path,
            "official_source_parent": VMRC_DOCKET_URL
            if "webapps.mrc.virginia.gov" in metadata["official_source_url"]
            else CHESTERFIELD_CIVICCLERK_URL
            if "chesterfieldcova.portal.civicclerk.com" in metadata["official_source_url"]
            else metadata["official_source_url"],
            "page_count": page_count(pdf_path),
            "file_size_bytes": file_size(pdf_path),
            "sha256": sha256(pdf_path),
        }
        records.append(record)

    records.sort(key=sort_key)

    hash_counts = Counter(record["sha256"] for record in records)
    hash_to_paths = defaultdict(list)
    for record in records:
        hash_to_paths[record["sha256"]].append(record["archived_path"])

    for record in records:
        sibling_paths = hash_to_paths[record["sha256"]]
        record["duplicate_count"] = hash_counts[record["sha256"]]
        record["duplicate_paths"] = sibling_paths
        record["is_duplicate"] = len(sibling_paths) > 1
        record["official_source_host"] = record["official_source_url"].split("/")[2]

    return records


def write_json(records: list[dict]) -> None:
    MANIFEST_JSON.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def write_csv(records: list[dict]) -> None:
    fieldnames = [
        "date",
        "year",
        "title",
        "agency",
        "originator",
        "description",
        "record_type",
        "status",
        "series",
        "series_order",
        "archived_path",
        "canonical_archived_path",
        "official_source_url",
        "official_source_parent",
        "official_source_note",
        "official_source_host",
        "summary_path",
        "page_count",
        "file_size_bytes",
        "sha256",
        "is_duplicate",
        "duplicate_count",
        "duplicate_paths",
        "sensitive_source_handling",
    ]
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["duplicate_paths"] = " | ".join(record["duplicate_paths"])
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def main() -> None:
    records = build_records()
    write_json(records)
    write_csv(records)
    print(f"Wrote {len(records)} records to {MANIFEST_JSON.relative_to(ROOT)}")
    print(f"Wrote CSV to {MANIFEST_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
