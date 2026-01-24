# Project Brief: Active Days Counter

**Date**: 2026-01-24
**Type**: PRODUCT_DEVELOPMENT
**Status**: Draft

## Overview

Build a feature that displays the total number of active days a user has spent on the portal. An "active day" is defined as any day where the user performs meaningful engagement actions such as clicks, views, or transactions. The counter will be displayed on the user profile/dashboard to motivate users through gamification.

## Problem Statement

Users currently have no visibility into their engagement history on the portal. Without this visibility, there's no natural motivation for users to return and engage consistently. A simple active days counter can provide a sense of accomplishment and encourage continued usage.

## Goals

- Increase user engagement by providing a visible metric of their portal activity
- Motivate users to return to the portal regularly
- Create a foundation for potential future gamification features
- Deliver a quick win that provides immediate value to all users

## Target Audience

All portal users - the feature will be visible to everyone using the platform.

## Scope

### In Scope

- Track user engagement actions (clicks, views, transactions) to determine active days
- Store and calculate total active days per user
- Display the active days counter on the user profile/dashboard
- Backend logic to determine what constitutes an "active" day

### Out of Scope

- Streak tracking (consecutive days)
- Badges or milestone achievements
- Rewards or points system
- Leaderboards or social comparison features
- Detailed activity analytics or breakdowns

## Constraints

- Timeline: 1-2 weeks (quick win approach)
- Keep the implementation simple and focused
- Must work for all existing portal users

## Success Criteria

- Active days counter is visible on user profile/dashboard
- Counter accurately reflects engagement-based activity
- Feature is shipped within 2 weeks
- No negative impact on portal performance

## Next Steps

1. Define which specific user actions qualify as "engagement" for active day tracking
2. Design the database schema for tracking daily activity
3. Implement backend logic for calculating active days
4. Create the UI component for the profile/dashboard
5. Test with sample users and deploy

---
*Generated via @new-project brainstorm agent*
