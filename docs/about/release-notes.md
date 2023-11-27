# Release Notes

## Wednesday 15 November 2023

**aimmo: 2.10.12, codeforlife-portal: 6.39.4**

* No longer gathering and processing school postcodes
* School countries are now optional
* UK schools can be linked to a county, which is also optional
* Fixed and issue with the flow for changing emails addresses
* Now tracking worksheet usage, worksheet badges and game load time in Kurono

## Friday 3 November 2023

**aimmo: 2.10.9, codeforlife-portal: 6.38.1, rapid-router: 5.15.5**

* Created levels 110-122 in Rapid Router, within Episode 12 as an introduction to While Loops.
* Added episodes 13-15 to the levels list and marked them as coming soon.
* Added a formal method to capture volunteer acceptance of contributing terms.
* Password fields in forms now have a "reveal password" icon.
* Removed autocomplete for some password fields.
* Increased the size of the Rapid Router level map so it takes up the whole section.
* Updated the button styles for the hint and level failure / completion popups in Rapid Router.

## Tuesday 17 October 2023

**aimmo: 2.10.7, codeforlife-portal: 6.37.1, rapid-router: 5.12.3**

* Introduced cows to levels 38, 39 and 47
* Removed the game-creator and moved its logic to the Django aimmo app

## Wednesday 20 September 2023

**codeforlife-portal: 6.37.0**

* Unverified users are now anonymised instead of deleted.
* Keep track of daily and total unverified users anonymisations.

## Tuesday 19 September 2023

**codeforlife-portal: 6.36.2**

Implemented a quick fix for the 2FA bug.

## Thursday 7 September 2023

**codeforlife-portal: 6.36.0**

Keep track of total registrations.

## Tuesday 5 September 2023

**codeforlife-portal: 6.35.3, rapid-router: 5.11.3**

* Added a comma in some of the Rapid Router levels instructions for better readability.
* Only the selected road type in the level editor has a border now to improve user experience.
* Created two automated email verification reminders for unverified users who registered 7 days ago and 14 days ago.
* Created an automated deletion job which deletes unverified users who have registered over 19 days ago.

## Monday 14 August 2023

**aimmo: 2.10.6, codeforlife-portal: 6.34.1**

* UK schools are now linked to a county.
* Kurono games are now stopped immediately upon deletion.
* Implemented a max limit of 15 for concurrent Kurono running games. Attempting to create or start a 16th game will show the user a friendly error message.
* Updated the starter code for worksheet 2 to reflect changes on Gitbook.

## Thursday 20 July 2023

**aimmo: 2.9.1, codeforlife-portal: 6.33.6, rapid-router: 5.11.1**

* Fixed a bug with the password strength indicator on password reset.
* Fixed a bug with the password reset email form.

## Thursday 29 June 2023

**rapid-router: 5.11.0**

Enabled secure boot for GKE nodes.

## Wednesday 28 June 2023

**aimmo: 2.9.0, codeforlife-portal: 6.33.0**

* Upgraded to Python 3.8.
* Added a check for commonly used passwords upon registration.

## Friday 16 June 2023

**aimmo: 2.8.7, codeforlife-portal: 6.31.1**

* Removed intermediate Teaching Resources pages, dropdowns now link directly to Gitbook.
* Shortened email verification links.
* Fixed Kurono cross-worksheet badges trigger bug.
* Testing out new GA4 script.

## Wednesday 31 May 2023

**codeforlife-portal: 6.30.11**

Fixed mistakenly removed riveted.js library.

## Thursday 25 May 2023

**aimmo: 2.8.5, codeforlife-portal: 6.30.10, rapid-router: 5.10.6**

Updated an outdated JS library.

## Sunday 30 April 2023

**aimmo: 2.7.0, codeforlife-portal: 6.30.4**

* Updated Kubernetes to 1.26 and Agones to 1.31.
* Addressed a number of security issues related to the clusters and node pools.
* Added a custom action in the Django admin panel allowing admins to bulk stop Kurono games.
* Added text in Terms of Use describing the school admin powers.

## Wednesday 26 April 2023

**aimmo: 2.5.20, codeforlife-portal: 6.30.2**

Implemented JWT tokens for the registration process, allowing users to have simultaneous valid email verification tokens on registration.

## Wednesday 12 April 2023

**aimmo: 2.5.19, codeforlife-portal: 6.29.9, rapid-router: 5.10.5**

* Fixed Avatar auth token generation when creating an Avatar in Kurono.
* Teachers can now access the account settings page even if they don't have a school.
* Updated the solution for level 43.
* Matched the green in the level editor sidebar to the one in the actual game.
* Verification emails are now sent before the newsletter confirmation emails.

## Tuesday 21 March 2023

**aimmo: 2.5.18, codeforlife-portal: 6.29.4**

* Updated text and padding of the Get Involved page.
* Added a "pause" functionality to the Kurono game - users can now pause their avatar, effectively stopping their code and the logs while the rest of the game carries on.

## Monday 13 March 2023

**aimmo: 2.5.16**

Updated the Kurono avatar marker - made it bigger, changed the model to the Kurono logo and added a bounce animation.

## Friday 10 March 2023

**rapid-router: 5.10.4**

* Reverted an issue introduced in the previous deployment which made the map no longer scrollable on tablets.
* Fixed the broken coin image that appears in the Episode title when all levels have been completed.

## Wednesday 8 March 2023

**rapid-router: 5.10.2**

Fixed some issues with the zoom buttons in Rapid Router, namely, the game doesn't randomly zoom in on the first input, and the buttons remain in the screen for all screen sizes.

## Tuesday 21 February 2023

**rapid-router: 5.10.1**

Fixed scoreboard bug whereby custom level names prevented the page from loading.

## Friday 17 February 2023

**aimmo: 2.5.15, codeforlife-portal: 6.29.3, rapid-router: 5.10.0**

* Fixed level editor disappearing scenery bug
* Updated introductory videos order in Rapid Router

## Wednesday 15 February 2023

**aimmo: 2.5.12, codeforlife-portal: 6.29.2, rapid-router: 5.9.1**

Fixed a broken DB migration.

## Monday 6 February 2023

**codeforlife-portal: 6.29.0**

Added ratelimit to the student login as well as the tracking for the lockout reset mechanic.

## Wednesday 25 January 2023

**codeforlife-portal: 6.28.3, rapid-router: 5.8.1**

Updated Privacy Notice with updated text and correct personal data information.

## Thursday 19 January 2023

**aimmo: 2.5.11, codeforlife-portal: 6.28.0, rapid-router: 5.8.0**

* Added cows and cow-related blocks to Rapid Router
* Implemented a data tracker for when users reset their passwords to unlock their accounts (teachers and independent students only)
* Having no nearby artefacts in worksheet 4 no longer raises an error which blocks the user from progressing, instead it prints out a more user-friendly warning.

## Wednesday 4 January 2023

**codeforlife-portal: 6.27.8, rapid-router: 5.7.4**

* Removed the snow in Rapid Router.
* Coding club page link now opens in the same tab as expected.

## Monday 19 December 2022

**codeforlife-portal: 6.27.7**

* Updated instructions for level control and added a usage tracker for it.
* Fixed broken independent student newsletter subscription.
* Added a link to the coding clubs page on the Get Involved page.

## Tuesday 6 December 2022

**codeforlife-portal: 6.27.3, rapid-router: 5.7.3**

* Brought back Rapid Rudolph
* Updated incorrect email address in privacy policy.
* Update Rapid Router UI including previous and next level buttons.

## Wednesday 16 November 2022

**aimmo: 2.5.10, codeforlife-portal: 6.27.1, rapid-router: 5.6.1**

* Teachers can now control which levels of Rapid Router are available on a per-class basis.
* Fixed missing padding in level editor.

## Monday 31 October 2022

**aimmo: 2.5.7, codeforlife-portal: 6.24.1**

Fixed a bug where old games would show in the Kurono games table.

## Tuesday 25 October 2022

**aimmo: 2.5.6, codeforlife-portal: 6.23.1, rapid-router: 5.5.2**

* Upgraded Kubernetes to version 1.23 on all Kurono resources.
* Admin teachers can now create Kurono games for their colleagues.
* Updated Rapid Router Python levels styles.

## Thursday 13 October 2022

**aimmo: 2.5.2, codeforlife-portal: 6.22.1, rapid-router: 5.5.1**

* Made the alert banner on the homepage dynamic.
* Fixed some bugs in the level editor.
* Admin teachers can now see, play, edit and delete any Kurono game in their school.

## Friday 7 October 2022

**codeforlife-portal: 6.21.0, rapid-router: 5.5.0**

Admin teachers can now see, play and share any custom level in their school.

## Friday 30 September 2022

**codeforlife-portal: 6.20.3**

Updated the Data Protection Officer's email address in the Privacy Policy.

## Wednesday 21 September 2022

**codeforlife-portal: 6.20.2**

Removed the Kurono maintenance banner.

## Thursday 15 September 2022

**codeforlife-portal: 6.20.1, rapid-router: 5.4.3**

* Fixed missing cookie banner and settings
* Fixed some UI bugs in Rapid Router

## Friday 9 September 2022

**codeforlife-portal: 6.19.1**

* Added code clubs page with free downloadable content
* Updated text to registration forms
* Fixed issue where the Kurono preview video would not load on the independent student dashboard

## Tuesday 6 September 2022

**aimmo: 2.4.6, codeforlife-portal: 6.18.3, rapid-router: 5.4.2**

* Fixed a major issue where deployment was broken by removing the legacy django-autoconfig package
* Added a banner on the homepage to warn users of ongoing issues with Kurono
* Updated session timeout to 30 minutes and added a 2 minute countdown to warn users of it
* Fixed some issues with Rapid Router button designs
* Users can now see their scores for custom levels on the scoreboard page

## Friday 5 August 2022

**codeforlife-portal: 6.16.0, rapid-router: 5.3.1**

* Admin teachers can now see and moderate all custom levels in their school
* Admin teachers can now see, accept and reject all external requests to their school's classes
* Updated Rapid Router icons
* Updated Rapid Router Python levels design and made each component resizable

## Wednesday 27 July 2022

**aimmo: 2.4.3, codeforlife-portal: 6.15.4**

* Admin teachers can now see, edit and delete all the classes in their school
* Admin teachers can now create a class for a fellow teacher
* Updated the "Make admin" popup

## Thursday 14 July 2022

**aimmo: 2.4.1, codeforlife-portal: 6.15.3, rapid-router: 5.1.0**

* Updated Rapid Router levels design
* Removed Dee from Python levels
* Added Bav the Brain to brainteaser levels
* Admin teachers can now see all classes in their school
* Gave admin teachers the ability to create classes for other teachers
* Updated the "Make teacher admin" popup
* Created child-friendly versions of the Privacy Policy and Terms of Use
* Independent students under 13 now need to provide their parents' or guardian's email address

## Friday 1 July 2022

**aimmo: 2.4.0, codeforlife-portal: 6.12.4, rapid-router: 4.4.1**

* Gave admin teachers the possibility to invite other teachers directly to their school
* Removed the ability to join another teacher's school by looking it up and sending a join request
* Added a confirmation popup to the independent student account deletion process
* Updated the teacher registration form and added a consent checkbox
* Added a one hour screen time warning popup
* Made the Rapid Router scoreboard clearer and easier to work with

## Tuesday 21 June 2022

**aimmo: 2.3.5, codeforlife-portal: 6.8.9**

* Removed newsletter signup for independent students
* Fixed registration boxes width

## Friday 17 June 2022

**aimmo: 2.3.4, codeforlife-portal: 6.8.8, rapid-router: 4.3.0**

* Added badges for challenge 1 in Kurono
* Independent students can now delete their accounts
* Signing up for the newsletter using the footer form now requires the user to be over 18
* Rapid Router solutions for levels 101-104 now have a main() method
* Teachers can now re-share the levels that are shared with them
* Fixed deleting workspaces in Rapid Router
* In Kurono, when moving towards is blocked by an avatar, a message is now displayed in logs
* Security updates

## Thursday 19 May 2022

**aimmo: 2.1.2, codeforlife-portal: 6.8.2**

* Add worksheet 4 for Kurono
* Security updates

## Thursday 12 May 2022

**codeforlife-portal: 6.6.0, rapid-router: 4.1.0**

* Update Rapid Router level 48 to include multiple houses
* Anonymise schools and classes without any active teachers

## Thursday 5 May 2022

**codeforlife-portal: 6.5.2**

* School is now anonymised when the last admin leaves and marked as inactive
* Fix email display and link

## Friday 29 April 2022

**aimmo: 2.0.4, codeforlife-portal: 6.4.4, rapid-router: 4.0.9**

* Anonymise classes instead of deleting them
* Update style and content of emails sent to users
* Update Pyodide to fix Kurono issue running on certain browsers
* Rename `v` variable in Rapid Router to `my_van`
* Fix multiple start blocks bug in Rapid Router

## Friday 8 April 2022

**codeforlife-portal: 6.3.1, rapid-router: 4.0.4**

* Delete account functionality for teacher
* Admin role is passed to the next teacher when admin account is deleted
* Fix bugs where deleted teachers were showing
* Update image credits and alt texts

## Friday 18 March 2022

**rapid-router: 4.0.2**

* Fixed Rapid Router not loading properly

## Friday 18 March 2022

**aimmo: 2.0.1, codeforlife-portal: 6.0.1, rapid-router: 4.0.1**

* Upgraded Django to version 3.2

## Monday 14 March 2022

**codeforlife-portal: 5.42.0**

* Independent student and login update to use email only and no username
* Added videos to Educate and Play pages

## Tuesday 8 March 2022

**rapid-router: 3.8.9**

Fixed student scoreboard not showing data.

## Friday 4 March 2022

**codeforlife-portal: 5.40.0**

Added Dotmailer address books integration on registration / newsletter subscription (user types).

## Thursday 3 March 2022

**codeforlife-portal: 5.39.1, aimmo: 1.4.11, rapid-router: 3.8.8**

* Scoreboard now does not display everything on page load
* Kurono student dashboard update
* Fixed Rapid Router freeze issue when using fast play
* Fixed Crowdin resources that were blocked

## Tuesday 1 March 2022

**rapid-router: 3.8.5**

Fixed Crowdin's In-Context translation tool.

## Monday 28 February 2022

**rapid-router: 3.8.3**

Fixed bug introduced with previous level 74 improvement.

## Friday 25 February 2022

**rapid-router: 3.8.2**

Improved Rapid Router level 74 solution.

## Thursday 24 February 2022

**codeforlife-portal: 5.37.2, aimmo: 1.4.10, rapid-router: 3.8.1**

* Thickened road divider lines in Rapid Router
* Updated remove / leave teacher page

## Wednesday 23 February 2022

**codeforlife-portal: 5.36.1, aimmo: 1.4.9, rapid-router: 3.8.0**

* Improved registration process
* Disabled local storage in Rapid Router

## Thursday 17 February 2022

**codeforlife-portal: 5.35.1, aimmo: 1.4.7, rapid-router: 3.7.8**

* Ensure no duplication of email when releasing student
* Cookies updates

## Monday 14 February 2022

**codeforlife-portal: 5.34.3, aimmo: 1.4.6**

* Data tracking for join and release of student
* Updated starter code for Kurono worksheet 3

## Wednesday 9 February 2022

**codeforlife-portal: 5.33.3**

Cleaned up some teacher and independent student accounts that had the same email.

## Monday 7 February 2022

**codeforlife-portal: 5.33.0**

User sessions will now expire on browser close.

## Thursday 3 February 2022

**codeforlife-portal: 5.32.3**

* Updated 2FA pages
* New registration for independent student or teacher now require unique email across the different account types

## Friday 28 January 2022

**rapid-router: 3.7.1**

Removed snow from Rapid Router.

## Thursday 27 January 2022

**aimmo: 1.4.5, codeforlife-portal: 5.32.0, rapid-router: 3.7.0**

* Updated OneTrust instance for cookie management
* Added scrollbar in Python pane in Rapid Router Python levels
* Made Python pane resizeable in Rapid Router Python levels
* Made email verification link expiry time explicit on verification page
* Redesigned password reset and email verification pages
* Redesigned Kurono teacher dashboard
* Redesigned level moderation page
* Fixed level moderation delete level bug
* Scoreboard page now loads all classes and levels data by default
* Deleting Kurono games now archives them instead of deleting them completely
* Upgraded to Kubernetes 21.7.0
* Tidied up independent student duplicate accounts with the same email

## Thursday 13 January 2022

**aimmo: 1.3.3, codeforlife-portal: 5.28.1, rapid-router: 3.5.7**

* Account details page updates
* Registration page update
* Kurono worksheet 2 starter code update
* Crashing, running a red light and running out of fuel in Rapid Router now count as an attempt
* Scoreboard filter update

## Friday 7 January 2022

**codeforlife-portal: 5.27.9, rapid-router: 3.5.5**

Fix scoreboard loading issues.

## Wednesday 5 January 2022

**codeforlife-portal: 5.27.8, rapid-router: 3.5.4**

* Fix alignment and text issues in edit class pages
* Fix scoreboard spacing and functional issues
* Allow logged in users to view other login pages

## Friday 31 December 2021

**codeforlife-portal: 5.27.5, rapid-router: 3.5.3**

* Update Scoreboard page with new designs and Improvements table
* Update all class edit pages

## Monday 20 December 2021

**aimmo: 1.3.2, codeforlife-portal: 5.26.14, rapid-router: 3.4.5**

* Remove Wagtail
* Align pages to container width
* Fix 2FA QR code not showing bug
* Fix 2FA banner bug
* Stick website footer to bottom of the screen
* Remove all Rapid Router resource pages and link to Gitbook instead
* Fix heading sizes on Play page

## Thursday 9 December 2021

**codeforlife-portal: 5.26.3, rapid-router: 3.4.4**

* Student login details CSV now includes student passwords and class link
* Fix for class code login issue
* Rapid Router functions renaming to be more descriptive
* Data and error logging

## Friday 3 December 2021

**codeforlife-portal: 5.24.2, rapid-router: 3.4.3**

* Enabled Rapid Rudolph :christmas\_tree:
* Updated Educate page
* Updated Play page
* Updated teacher and independent student navigation bars&#x20;
* Fixed alignment issues on student Kurono dashboard
* Fixed alignment of header and footer
* Fixed teacher dashboard and Kurono page
* Fixed size of table buttons

## Friday 26 November 2021

**codeforlife-portal: 5.21.3, rapid-router: 3.4.1**

Further CSP fixes.

## Thursday 25 November 2021

**aimmo: 1.3.0, codeforlife-portal: 5.21.2, rapid-router: 3.4.0**

* Home Learning page update and Independent student resources
* Fix for deleted students appearing at places
* Class code is now case insensitive plus related fixes
* Implemented CSP header
* Kurono worksheet updates - moved from model to a data file
* Privacy policy and Terms of use pages design updates

## Friday 19 November 2021

**codeforlife-portal: 5.17.1, rapid-router: 3.3.1**

* Updated Rapid Router level selection page
* Removed django-hijack

## Friday 12 November 2021

**codeforlife-portal: 5.17.0**

Added student login type data.

## Friday 5 November 2021

**rapid-router: 3.2.0, codeforlife-portal: 5.16.3**

* Moved and linked Kurono resources to Gitbook
* Updated teacher onboarding pages
* Updated About Us page
* Updated student dashboard including independent student
* Updated lockout page
* Removed Ocado logos from in-game images
* Added functionality to import students from CSV file
* Fix for class deletion

## Wednesday 20 October 2021

**rapid-router: 3.1.0, codeforlife-portal: 5.10.0**

* Updated most of the Rapid Router level help texts (morning)
* Updated student deletion data (afternoon)

## Monday 18 October 2021

**codeforlife-portal: 5.9.0**

Added school and class creation time and data.

## Friday 15 October 2021

**aimmo: 1.1.0, codeforlife-portal: 5.8.0**

* Updated reminder cards design
* Replaced `IndexError` of `scan_nearby` returned list with a more meaningful error
* Fixed "Update account details" in the account dropdown
* Added login metrics
* Upgraded reportlab and pillow libraries

## Monday 11 October 2021

**codeforlife-portal: 5.6.1, rapid-router: 3.0.5**

* Student login updated - option with class code or with direct link
* Updated page with student login details
* Updated class code format and student password policy
* Split teacher dashboard in 3 tabs and updated designs
* Updated teacher password policy
* Updated login pages to have branding shapes

## Monday 27 September 2021

Updated Dotmailer's "Thanks for staying" campaign ID env var to point to the new one, which is aligned to the new design.

## Thursday 23 September 2021

**codeforlife-portal: 5.2.3, rapid-router: 3.0.4**

* Fixed some issues with page banners and header styles
* Improved 2FA pages UI to match new styles
* Disabled Turkish language localisation in Rapid Router after reports of it causing issues in classrooms

## Wednesday 15 September 2021

**codeforlife-portal: 5.2.1, rapid-router: 3.0.3**

* [@sebp999](https://github.com/sebp999): Fixed bug with deleting Rapid Router custom level
* Added index to Terms of Use
* Removed country flag from Update School form
* Header image repositioning and other header updates

## Friday 10 September 2021

**codeforlife-portal: 5.0.1**

Button and table display fixes.

## Monday 6 September 2021

**aimmo: 1.0.0, codeforlife-portal: 5.0.0, rapid-router: 3.0.0**

* Updated website logo, design and style
* Removed teacher title
* Updated privacy policy

![New website design](../.gitbook/assets/www.codeforlife.education\_.png)

## Monday 23 August 2021

**codeforlife-portal: 4.34.0, rapid-router: 2.7.14**

* [@sebp999](https://github.com/sebp999): Disable saving and loading of workspace when user is not logged in
* [@sebp999](https://github.com/sebp999): Disable save and load buttons in the game template when user is not logged in

## Thursday 5 August 2021

**codeforlife-portal: 4.33.0**

Added Get Involved and Contributor pages.

## Monday 26 July 2021

**aimmo: 0.69.19, codeforlife-portal: 4.32.4, rapid-router: 2.7.13**

Improved user experience of login forms.

## Thursday 22 July 2021

**aimmo: 0.69.18, codeforlife-portal: 4.32.3**

* Kurono games now stop properly
* Fixed empty game name bug
* Dockerised portal for development

## Wednesday 7 July 2021

**aimmo: 0.69.14, codeforlife-portal: 4.31.4, rapid-router: 2.7.12**

* Changed Kurono game load text to be more informative
* Improved load time of Kurono games

## Monday 28 June 2021

**codeforlife-portal: 4.31.2**

Enforced account's email verification on login.

## Friday 25 June 2021

**codeforlife-portal: 4.31.1, rapid-router: 2.7.11**

* Additional hint text for Rapid Router level 80 onwards
* Top navigation bar fix on onboarding phase

## Wednesday 23 June 2021

**codeforlife-portal: 4.30.13, rapid-router: 2.7.10**

* Display updates to the Rapid Router 'if else' block: clearer separation, clearer hints
* Security header update

## Thursday 17 June 2021

**codeforlife-portal: 4.30.12, rapid-router: 2.7.7, aimmo: 0.69.11**

* Upgrade to Django 2.2.24
* Prevent changing an account's email address to that of another account's

## Thursday 10 June 2021

**codeforlife-portal: 4.30.8, rapid-router: 2.7.5, aimmo: 0.69.8**

* Prevent concurrent login sessions for the same user
* Security fixes and documentation updates

## **Friday 21 May 2021**

**codeforlife-portal: 4.29.2, rapid-router: 2.7.4, aimmo: 0.69.3**

* Added ability to edit saved custom levels
* Fixed invalid character bug

## **Friday 21 May 2021**

* Fixed ReCaptcha bypass issue
* Added ratelimit to sensitive forms and re-implemented 24 hour lockout
* Fixed session not invalidated after password change issue
* Removed autocomplete from forms
* Added warning banner for email verification

![](https://assets.sutori.com/user-uploads/image/b2d431a5-aaa4-403d-91be-e5e0aa4e050d/cybersecurity-vs-information-security-illustration.jpeg)

## **Friday 7 May 2021**

Security fixes and JavaScript updates

![](https://assets.sutori.com/user-uploads/image/629c4170-70ca-4c42-aeb2-0b47785728b6/kisscc0-cute-lock-icons-5b37078a752296.5931807415303330664798.png)

## **Thursday 22 April 2021**

* Added Dotmailer consent renewal form
* Fixed interchangeable GETs/POSTs issues

![](https://assets.sutori.com/user-uploads/image/43cc7bae-a80f-422d-8018-84f8b4434d67/Selection\_357.png)

## **Monday 19 April 2021**

* OneTrust Cookie Management
* Updated Privacy Policy

![](https://assets.sutori.com/user-uploads/image/c5b25772-ce88-4661-9f80-43d8875f401f/Screenshot%20from%202021-04-19%2017-16-44.png)

## **Thursday 15 April 2021**

Removed the admin login page! Admin access now requires a superuser profile with 2FA enabled.

![](https://assets.sutori.com/user-uploads/image/44fc94fd-33a8-4a43-addc-048a0f24337f/shutterstock\_346773854.jpeg)

## **Friday 9 April 2021**

* Fixed a link in the Worksheet 3 resources.
* Made portal only send Google Analytics events in prod environment.

![](https://assets.sutori.com/user-uploads/image/d86474b6-359f-4ff2-a81d-c63673c4dc3d/Screenshot%20from%202021-04-15%2017-45-30.png)

## **Thursday 1 April 2021**

* Released Kurono Challenge 3!
* Added MoveTowardsAction and scan\_nearby methods to Kurono.
* Challenge 3 has a new theme and two new different artefacts.
* PDFs and solutions file have been updated with Challenge 3.
* Not an April Fools, the above actually happened 🙂

![](https://assets.sutori.com/user-uploads/image/f06a2806-b6ba-468f-b558-ae52d7259e13/ancient\_active\[1].png)

## **Friday 26 March 2021**

* Fixed worksheet selection bug.
* Fixed Recaptcha dual-script bug.

![](https://assets.sutori.com/user-uploads/image/9600b544-ae30-47df-b31b-bee186683723/Selection\_346.png)

## **Monday 8 March 2021**

* Revamped the admin login page.
* Added 2FA to the admin login form for accounts with 2FA.

![](https://assets.sutori.com/user-uploads/image/3f1eac09-9c7a-4a40-9c6c-1475813510cd/Selection\_321.png)

## **Friday 5 March 2021**

Fixed pickups not spawning.

![](https://assets.sutori.com/user-uploads/image/1b2c624f-f723-4734-9fbe-95c18b3d0daf/Screenshot%20from%202021-03-09%2013-26-22.png)



## **Monday 1 March 2021**

Navigation and text updates on Kurono pages.

![](https://assets.sutori.com/user-uploads/image/b2f2ccb3-0be3-4c30-b4bf-eadde6937d56/Screenshot%202021-03-02%20at%2014.57.07.png)

## **Monday 1 March 2021**

Consent data when signing up to newsletter is now saved.

![](https://assets.sutori.com/user-uploads/image/c71a68ac-8aa0-42a6-8603-c579e869e979/Selection\_297.png)

## **Monday 1 March 2021**

Agones has been integrated to improve game creation and loading.

![](https://assets.sutori.com/user-uploads/image/5db142ce-c6dc-4a07-ae32-3f715ea5966d/Screenshot%202021-03-02%20at%2014.53.42.png)

## **Monday 1 March 2021**&#x20;

* Stats on Home and About page updated with the latest data.
* Copyright year in the footer now updates automatically.

![](https://assets.sutori.com/user-uploads/image/9807bfd0-2832-433d-bbe9-dbcf7217b589/Selection\_296.png)

## **Monday 1 March 2021**

Console update to increase font size and make colour contrast more accessible.

![](https://assets.sutori.com/user-uploads/image/3356b514-6e03-4ba5-89be-6cff4ac403b4/Screenshot%202021-03-01%20at%2018.30.06.png)

## **Tuesday 9 February 2021**

Fixed the "Trash Can" bug.

![](https://assets.sutori.com/user-uploads/image/af4a35d9-d95e-4f98-9872-ab0ce5ebb6b7/Selection\_268.png)

## **Tuesday 2 February 2021**

* Finished updating games table on Teacher Kurono Dashboard page.
* Added the Kurono solutions file to the Kurono Packs page.

![](https://assets.sutori.com/user-uploads/image/51d02723-360d-44d7-a3e3-4a4e10fe2f47/Selection\_260.png)

## **Friday 29 January 2021**

* Updated the Teacher Kurono Dashboard page by simplifying the resources section and add the "Add Class" and "Challenge" dropdowns.
* Updated Recaptcha script in hope to fix Recaptcha issues in certain countries.

![](https://assets.sutori.com/user-uploads/image/5ff6c843-a099-4991-87a7-1a6ba9ca7890/screencapture-codeforlife-education-teach-kurono-dashboard-2021-02-01-15\_49\_01.png)

## **Thursday 21 January 2021**

* Added Kurono Resources.
* Added Kurono Teaching Packs.
* Reset Code has been fixed in Kurono - it now resets the code to the Worksheet's starter code.

![](https://assets.sutori.com/user-uploads/image/e110007e-dbf0-4d44-985e-57c3b7bd1d78/Screenshot%202021-01-21%20120430.jpeg)

## **Wednesday 30 December 2020**

The sub nav has been fixed - it is now visible on mobile!

![Subnav on mobile](https://assets.sutori.com/user-uploads/image/80fd5cfb-0892-4537-86d4-fa72ab460301/Selection\_215.png)

## **Wednesday 23 December 2020**

We upgraded to Django 2.2!&#x20;

![](https://assets.sutori.com/user-uploads/image/b5bcb426-acc5-4322-8e42-90ba8bcb223f/django2.png)

## **Monday 14 December 2020**

Rapid Rudolph has returned!

![](https://assets.sutori.com/user-uploads/image/255ae519-015d-4ca4-8db7-72527aee9501/Selection\_205.png)

## **Monday 14 December 2020**

The Kurono "Add Game" form was improved by clarifying the labels

