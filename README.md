# Philadelphia Pointing Span Test (PPST)

A Django-based web application for administering the Philadelphia Pointing Span Test, a clinical neuropsychological assessment tool. Built by a 7-person Agile team at Rowan University as a senior capstone project.

## Overview

The PPST provides a distraction-free interface for patients to complete pointing span assessments, and a secure portal for clinicians to create tests, review results, and export performance data.

## My Contributions

As one of two backend developers on the project, I owned the following work:

- **Bilingual text-to-speech system** — Implemented English/Spanish TTS across all patient-facing test pages to expand accessibility for non-English speakers
- **CSV export endpoint** — Built the data export pipeline allowing clinicians to download structured patient response data for research and clinical analysis
- **Filter views** — Authored the clinician-facing filter view for querying and sorting test results by patient, date, and language
- **Stimulus/Response models** — Designed and implemented core Django models for storing test stimuli and patient responses
- **Seed data command** — Created a Django management command to populate test data for development and demo environments

Collaborated using GitHub pull requests with code review by teammates.

## Features

- Bilingual test delivery (English and Spanish) with text-to-speech audio
- CSV data export for research and clinical analysis
- Filtered test views for clinician dashboards
- Doctor dashboard with patient management
- Seed command for test data population
- Secure authentication for clinicians and administrators

## Tech Stack

- **Backend:** Python, Django, PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Django built-in authentication system

## Team

| Name | Role |
|------|------|
| Sean Daly | Backend Developer |
| John Bermudez | Project Lead |
| Niqolas Gonzales | Frontend Developer |
| Christian Police | Frontend Developer |
| James Hayes | Backend Developer |
| Udoka Njoku | Frontend Developer |
| Jenna Princiotta | Frontend Developer |

## Institution

Rowan University — Senior Capstone Project, 2026
