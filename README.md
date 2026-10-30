What This App Does? 
===================
This application generates realistic, localized fake user profiles (for regions like English/US or German/Germany) and stores them in an Aiven MySQL database.
The main goal is strict consistency:

Every time you look up a specific combination of Locale, Seed, and Batch Index, the app always displays the exact same 10 users.

If you switch to a batch that hasn't been created yet (for example, Batch 50), the app automatically generates and saves 10 new users on the fly.

How to Use the App (User Guide)
==============
1. Open the app in your browser. 
2. Select Locale / Region: Choose between English (en_US) or German (de_DE). 
3. Enter a Seed: Type any number (e.g., 42 or 50). This acts as the random pattern blueprint.
4. Enter a Batch Index: Type any number (e.g., 1, 2, up to infinity) to navigate through different pages of 10 unique users. 
5. Click  View / Load Batch to display that specific batch.

Under the Hood (How It Works)
================
1. Deterministic Generation (The "Faker" Logic)

Instead of picking random users completely at random, the app uses an MD5 cryptographic hash built from your inputs:

Seed String = Locale + Seed + Unique User Index

This hash creates a fixed random sequence, meaning returning to Batch 2 later will always show the exact same people.

2. Biometric Data (Height & Weight)
   ===================
Heights and weights are calculated using a bell curve (Gaussian distribution) so they look natural:
Height: Averaged around 175 cm (clamped safely between 140 cm and 210 cm).
Weight: Averaged around 70 kg (clamped safely between 40 kg and 140 kg).

4. Realistic Coordinates (No Pole Bunching)
   ==================
Instead of picking flat grid coordinates (which makes points bunch up unnaturally near the North/South poles), the app uses a spherical distribution algorithm (Constant PDF) to scatter coordinates evenly across the globe.

6. Localized Names & Addresses
   =================
English (en_US): Generates typical American names, street names (e.g., Main St), postal codes, and phone numbers (+1 ...).
German (de_DE): Generates typical German names, street names (e.g., Hauptstraße), 5-digit postal codes, and phone numbers (+49 ...).
