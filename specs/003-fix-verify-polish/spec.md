# Feature Specification: Fixes & Polish (Verify, Extract, Embed)

**Feature Branch**: `003-fix-verify-polish`
**Created**: 2025-12-15
**Status**: Draft
**Input**: Fix Verify payload decoding, clarify Extract vs Verify, add download button, fix Extract upload bug, remove Attack Simulator from Embed.

## User Scenarios & Testing

### User Story 1 - Reliable Blind Verification (Priority: P1)

As a user, I want the "Verify" function to accurately decode the watermark text from a suspect image, so that I can trust the verification result. Currently, it returns random characters.

**Why this priority**: The core value of "Verify" is broken if it returns garbage.

**Independent Test**:
1.  Embed "Test1234" into an image.
2.  Upload the result to the Verify tab.
3.  Result should display "Test1234", not random symbols.

**Acceptance Scenarios**:
1.  **Given** a watermarked image with text "Secret", **When** I verify it without modification, **Then** the system returns "Secret".
2.  **Given** a watermarked image, **When** I verify it, **Then** the confidence score reflects the decoding quality.

### User Story 2 - Embed Tab Usability (Priority: P2)

As a user, I want to download the watermarked image directly from the Embed tab and not be distracted by the Attack Simulator there.

**Why this priority**: Improves the primary workflow (Embed -> Download).

**Independent Test**:
1.  Go to Embed tab.
2.  Embed a watermark.
3.  Click "Download" button.
4.  Verify Attack Simulator is NOT present in this tab.

**Acceptance Scenarios**:
1.  **Given** a generated watermark, **When** I click "Download", **Then** the browser downloads the PNG file.
2.  **Given** the Embed tab, **When** I look at the UI, **Then** I do not see the Attack Simulator component.

### User Story 3 - Fix Extract Uploads (Priority: P2)

As a user, I want to upload both "Original" and "Suspect" images in the Extract tab without one overwriting the other or causing errors.

**Why this priority**: The Extract function is currently unusable due to this bug.

**Independent Test**:
1.  Go to Extract tab.
2.  Upload "Original.png".
3.  Upload "Suspect.png".
4.  Both files remain selected and distinct.

**Acceptance Scenarios**:
1.  **Given** the Extract tab, **When** I select an Original file and then a Suspect file, **Then** both files are correctly stored in the state and sent to the API.

### User Story 4 - UI Clarity (Priority: P3)

As a user, I want clear distinction between "Extract" (Requires Original) and "Verify" (Blind) in the UI.

**Why this priority**: Reduces user confusion about which tool to use.

**Independent Test**:
1.  View the navigation or tab headers.
2.  See clear labels/tooltips explaining the difference.

**Acceptance Scenarios**:
1.  **Given** the main navigation, **When** I hover or view the tabs, **Then** "Extract" is labeled as "With Original" (or similar) and "Verify" as "Blind / No Original".

## Requirements

### Functional Requirements

-   **FR-001**: The `Verify` logic MUST use a robust decoding method (possibly adding error correction or a fixed preamble) to ensure the extracted text is correct.
-   **FR-002**: The `Embed` tab MUST include a "Download" button for the processed image.
-   **FR-003**: The `Embed` tab MUST NOT render the `AttackSimulator` component.
-   **FR-004**: The `Extract` tab MUST correctly handle two distinct file inputs (Original and Suspect) without state conflict.
-   **FR-005**: The UI MUST explicitly label the difference between Extract (Reference-based) and Verify (Blind).

### Technical Constraints & Decisions

-   **Payload Encoding**: To fix the garbage output, the system must implement a robust method to distinguish valid watermarks from random noise.
    -   The solution should include a **distinct header or preamble** (e.g., a specific character sequence) to validate the presence of a watermark.
    -   If the header is not detected, the system must return a "No Watermark Detected" status instead of attempting to decode random noise.
-   **State Management**: The application must correctly handle independent file selections for "Original" and "Suspect" images without cross-contamination.

### Key Entities

-   **WatermarkPayload**: Logical structure containing `[Header][Length][Data]`.

## Success Criteria

-   **Verification Accuracy**: 100% for undistorted images, >80% for rotated images (if alignment works).
-   **Usability**: Users can complete the Embed -> Download flow in < 10 seconds.
-   **Bug Fix**: Extract tab successfully processes a request with two valid images.

## Assumptions

-   The "garbage" text is due to interpreting noise as ASCII. Adding a header/checksum will solve the "false positive" text issue.
