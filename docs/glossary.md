# DDD Glossary - AI Code Review System

## System Workflow

The AI Code Review system is fully automated and based on 5 key domain policies that orchestrate the entire code analysis process:

### 1. Auto Start Analysis Policy
**Trigger:** `ProjectTracked` event
**Action:** Automatically starts analysis for new Pull Requests according to the project's Policy configuration
**Goal:** Ensuring that every new PR is automatically analyzed without user intervention

### 2. Auto AI Analysis Policy
**Trigger:** `AnalysisCreated` event
**Action:** Automatically triggers the AI service to conduct code analysis and generate comments
**Goal:** Immediate handoff of code to AI analysis without delays

### 3. Auto Notification Policy
**Trigger:** `AnalysisApproved` event
**Action:** Automatically sends approved comments to the external repository (GitHub/GitLab/Bitbucket)
**Goal:** Automatic publication of analysis results in the Pull Request

### 4. Auto Retry Send Policy
**Trigger:** `SendAttemptFailed` event
**Action:** Automatically retries sending comments when external API communication fails
**Goal:** Ensuring reliable delivery of comments despite transient network issues

### 5. Auto Retry Analysis Policy
**Trigger:** `AdditionalContextAdded` event
**Action:** Automatically triggers re-analysis when user adds additional context
**Goal:** Enabling iterative improvement of analysis with additional context

**Complete flow:**
1. Developer adds project → `ProjectTracked` → Auto Start Analysis
2. New PR → `AnalysisCreated` → Auto AI Analysis → `CommentsGenerated`
3. **Developer reviews comments:**
   - Must set status for each comment (approved/rejected)
   - After reviewing all comments → `AllCommentsReviewed`
4. **Developer has 3 options:**
   - **Option A:** Accept analysis → `AnalysisApproved` → Auto Notification
   - **Option B:** Reject analysis → `AnalysisRejected` (process ends)
   - **Option C:** Add context → `AdditionalContextAdded` → Auto Retry Analysis (return to step 2)
5. On send failure (Option A) → `SendAttemptFailed` → Auto Retry Send

## Aggregates

### Project
Aggregate representing a single code repository connected to the AI Code Review system.

**Attributes:**
- ID - unique repository identifier (value object)
- Repository ID (id from external repository)
- Repository Name - repository name
- Provider - service provider (GitHub, GitLab, Bitbucket)
- Owner - repository owner
- URL - repository address
- Policies - analysis creation policies (value object)
- Rules - code review rules (value object)

**Business behaviors:**
- `update_rules()` - update code review rules
- `start_analysis()` - factory method for Analysis aggregate

**Domain events:**
- `ProjectTracked` - project was added to tracking
- `ProjectDeleted` - project was deleted
- `ProjectRulesUpdated` - project rules were updated

**Business constraints:**
- Provider must be one of the supported ones (GitHub, GitLab, Bitbucket)
- Repository existence must be verified during creation
- **MVP: Only public GitHub repositories are supported**
- Policies are required (default, not user-selectable)
- Rules are not required (default values are set)
- Project deletion causes deletion of all associated analyses
- No restrictions on editing policies (at current stage)
- "Dead" projects (without activity) are acceptable (MVP)
- Project is the aggregate root - controls access to its value objects

### Analysis
Aggregate representing one analysis of a specific Pull Request.

**Attributes:**
- ID - unique analysis identifier
- Project ID - associated project identifier
- Pull Request ID - Pull Request identifier
- Diff - code differences from the Pull Request
- Status - current analysis status (value object)
- Context - analysis context (value object)
- Created At - creation timestamp
- Ready At - ready for review timestamp
- Comments - collection of AI-generated comments (entities, lazy loaded)

**Business behaviors:**
- `conduct_analysis()` - set analysis to "ready for review" status
- `approve_analysis()` - approve analysis by user
- `reject_analysis()` - reject analysis
- `retry_analysis()` - re-analyze with additional context
- `delete_analysis()` - delete analysis
- `create_comment()` - factory method for Comment within analysis

**Creation methods:**
1. **Automatic** - for new/modified PR (according to project Policies)
2. **By user** - for re-analysis with new context (respecting Policies)

**Domain events:**
- `AnalysisCreated` - analysis was created
- `CommentsGenerated` - AI generated comments
- `AllCommentsReviewed` - all comments have been reviewed
- `AnalysisApproved` - analysis was approved
- `AnalysisRejected` - analysis was rejected
- `AnalysisDeleted` - analysis was deleted
- `AnalysisRetried` - analysis was retried
- `ContextAdded` - additional context was added

**Business constraints:**
- Analysis must always be associated with a specific Pull Request
- Cannot exist without Project
- Retrying analysis = creating new Analysis + rejecting previous one
- Creation must comply with project Policies
- **Approval requires: all Comments must have status (rejected/approved) + min. 1 Comment approved**
- **Comments can only be modified when Analysis status is "ready for review"**
- Analysis is the aggregate root - controls access to its entities

## Entities

### Comment
Entity representing an AI-generated comment within an analysis.

**Attributes:**
- ID - unique comment identifier
- Analysis ID - associated analysis identifier
- Content - comment content
- File Path - file path
- Line Number - line number
- Severity Level - importance level
- Status - comment status (value object)
- Created At - creation timestamp
- Modified At - last modification timestamp

**Business behaviors:**
- `update_content()` - modify comment content by user
- `set_status()` - set status (approved/rejected/pending)

**Domain events:**
- `CommentConfirmed` - emitted when status is set to approved
- `CommentModified` - emitted when content is changed
- `CommentDeleted` - emitted when status is set to rejected

**Business constraints:**
- Comment can only be modified when Analysis has "ready for review" status
- Status can be changed freely (approved ↔ rejected ↔ pending)
- Content can be edited by user
- Comment cannot be deleted, only rejected
- User cannot add their own comments (MVP)

## Value Objects

### ID
Unique repository identifier in the format provider:owner:repo_id.

**Structure:**
- Format: `{provider}:{owner}:{repo_id}`
- Example: `github:microsoft:typescript`

**Constraints:**
- Provider must be a supported provider
- Owner and repo_id cannot be empty
- Identifier must be unique across the entire system

### AnalysisStatus
Status determining the current stage of analysis.

**Possible values:**
- `created` - analysis was created but not conducted by AI
- `ready for review` - AI completed work, comments were generated
- `approved` - all comments were reviewed by user
- `rejected` - user definitively rejected the analysis or retried it

**Transition rules:**
- created → ready for review (after comment generation)
- ready for review → approved (after reviewing all comments)
- ready for review → rejected (by user)
- approved → rejected (when retrying analysis)

### CommentStatus
Status determining the state of comment review by user.

**Possible values:**
- `pending` - comment awaits review (default status)
- `approved` - comment accepted by user
- `rejected` - comment rejected by user

**Transition rules:**
- pending → approved (user accepts comment)
- pending → rejected (user rejects comment)
- approved ↔ rejected (user can change decision)
- Status change only possible when Analysis has "ready for review" status

### Diff
Value object representing code differences from Pull Request in normalized format.

**Responsibility:**
- Normalizing differences from various providers (GitHub, GitLab, Bitbucket) to common standard
- Providing unified interface for analyzing code changes
- Encapsulating parsing and validation logic for differences

**Constraints:**
- Immutable - cannot be modified after creation
- Must be properly parsed from source format
- Contains only data necessary for code analysis

### Context
Analysis context containing information helpful for AI.

**Structure:**
- Comments from previous analysis (if exists)
- List of additional texts entered by user
- Pull Request metadata

**Responsibility:**
- Providing AI with broader context about Pull Request
- Preserving history from previous analyses
- Enabling user influence on analysis

### Policies
Rules determining how analyses are created and managed in the project.

**Structure:**
- Pull Request Policy - enum determining when to create analyses
- Retry Limit Type - enum determining type of retry limit
- Retry Limit Value - limit value (MVP: maximum 2)

**Business constraints:**
- Pull Request Policy can be extended with new options
- Retry Limit Value currently limited to maximum 2 attempts
- Policies are set by default (may depend on subscription plan in future)

### Rules
Rules and conventions for conducting code review.

**Structure:**
- Text list containing project rules

**Responsibility:**
- Defines conventions for adding comments to code review
- Determines project standards and rules
- Contains repository-specific rules
- Easy to manage by users
- Optional (system will set default values if not specified)

## Error Handling

### Errors

#### SendAttemptFailed
**When:** Failure to send comments to external repository
**Data:** Error details, attempt number, repository details
**Follow-up:** Trigger for Auto Retry Send Policy

#### RetryLimitExceeded
**When:** Exceeding maximum number of re-analysis attempts
**Data:** Analysis ID, retry count, last error
**Follow-up:** Redirect to manual intervention

### Error Handling Strategy

1. **Idempotency:** All operations designed as idempotent
2. **Circuit Breaker:** For communication with external services
3. **Dead Letter Queue:** For events that failed to process
4. **Compensation Actions:** For rollback of complex operations
5. **Monitoring:** Comprehensive logging and metrics for all hot spots

## Domain Services

### ProjectCreationService
Service responsible for creating new projects.

**Responsibility:**
- Verifying repository existence in external system
- Checking external invariants
- Coordination with ProjectFactory

### ProjectFactory
Factory responsible for constructing Project aggregate.

**Responsibility:**
- Validating consistency of internal invariants
- Creating Project aggregate with correct value objects
- Setting default Policies and Rules

### ProjectDeletionService
Service responsible for deleting projects.

**Responsibility:**
- Deleting project along with all associated analyses
- Coordinating deletion process between aggregates

### AnalysisRetryService
Service responsible for re-analysis with additional context.

**Responsibility:**
- Retrieving comments from previous analysis
- Retrieving analysis to copy
- Delegating to Analysis creation of copy with new context
- Calling `conduct_analysis()` on new analysis
- Rejecting previous analysis

### CommentCreationService
Service responsible for creating comments based on AI results.

**Responsibility:**
- Coordinating comment creation process
- Using AICodeReviewPort to receive comment data
- Calling factory method `create_comment()` on Analysis aggregate
- Mapping structures from port to Comment entities

### AICodeReviewService
Domain service responsible for orchestrating AI code analysis process.

**Responsibility:**
- Preparing data for AI service (Diff, Context, Rules)
- Using AICodeReviewPort to communicate with external AI service
- Coordination between Analysis, Project and CommentCreationService
- Handling comment creation flow
