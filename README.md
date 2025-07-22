# service_queue

ระบบจองบัตรคิวตัวอย่างด้วย Python Flask

This repository contains a sample queue booking system. The provided
`schema.sql` defines the MySQL schema for a municipal queue database.

## Getting Started

1. Install dependencies (only Flask is required)::

    pip install flask

2. Run the development server::

    python app.py

The application exposes two main pages:

- `/` – the public page where citizens can book a queue number.
- `/staff` – the staff page showing all queue bookings. Access requires
  authentication via the `/login` route which simulates an SSO system.

## Notes

This is a minimal demonstration. The SSO flow is stubbed with a simple
`/login?user=some_id` query parameter to represent an SSO callback.
Integrate with your actual SSO provider as needed.
