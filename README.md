# Introduction
## Background Information
Solid waste, which refers to unwanted and unusable materials that we get rid of, presents a 
major challenge in Nairobi City County. The improper practices related 
to managing waste, such as handling, storing, collecting, transporting, and disposing of it, result 
in risks to public health and harm to the environment. Nairobi produces an 
astounding 4,016 tonnes of municipal solid waste every day, a number forecasted by Allison and likely influenced by factors like population growth, urbanization, changes in 
lifestyle, and industrial activities. 

Illegal dumping is a significant issue, with traditional waste collection services struggling to keep up. 
According to BNK Njoroge, M. Kimani, and D. Ndunge, an estimated 2,690 tonnes of 
garbage remain uncollected daily. This waste is often either burned or disposed of improperly, 
worsening the situation. The negative effects of improper waste disposal are severe, impacting 
both public health and the environment, particularly in developing countries and urban areas.Limited citizen involvement poses a significant 
challenge in addressing the waste management challenges in Nairobi. 

Informal settlements bear the brunt of this issue, as overflowing bins and uncollected garbage are a common occurrence. 
The lack of a centralized reporting system prevents authorities from fully understanding the 
scale of the problem, thus hindering the implementation of specific solutions. When residents 
feel disconnected from the waste management process, they may develop feelings of apathy or 
helplessness, ultimately failing to hold authorities responsible for efficient waste collection and 
disposal while there are efforts in place to encourage public engagement in waste management, they often do not meet expectations. Social media, a widely 
used platform for highlighting waste-related issues, lacks a centralized system for monitoring 
and solving these issues. 

Although initiatives such as community clean-up events and 
awareness campaigns are praiseworthy, their impact and sustainability are often limited. A more structured and centralized approach to 
involving citizens is urgently required. The proposed solid waste reporting system, Ripoti Taka, 
has the potential to transform waste management in Nairobi. Through collaboration with the 
city authorities, empowering residents to report waste concerns, and enhancing transparency in 
the process, Ripoti Taka could result in a 14% enhancement in solid waste management.

## Problem Statement
Poor solid waste management in Nairobi is characterized by rudimentary waste storage, lack 
of engineered landfill facilities, environmental concerns, and a policy-action gap due to non cooperation and poor law enforcement. The ideal scenario for solid waste 
management involves active citizen participation throughout the county. However, the reality 
is one of limited and unstructured citizen participation amid poor solid waste management. 
Informal channels like social media platforms are used for reporting but lack a centralized 
system for tracking and resolving problems. Localized initiatives exist but have limited reach 
and sustainability. 

This lack of structure creates an information gap: authorities lack real-time 
data on problem areas, hindering targeted solutions. The limited citizen participation in 
Nairobi's waste management system hinders efforts towards achieving sustainable waste 
management. This research project proposes the development and implementation of a web 
application called Ripoti Taka to bridge this gap. Ripoti Taka will empower citizens to report 
waste issues, fostering collaboration with authorities and promoting transparency. By 
addressing this critical problem, Ripoti Taka has the potential to transform waste management 
in Nairobi, leading to a cleaner and healthier environment for all residents.
## Objectives
### General Objective
To develop a web application that allows residents within a specific area to report poorly 
disposed solid waste for collection.
### Specific Objectives
* To study and investigate the current state of public participation in solid waste 
management in Nairobi City County
* To investigate the challenges facing the current solid waste reporting channels.
* To study how existing technologies have been used in solid waste management.
* To design and develop a web-application to assist in the reporting of poorly 
disposed waste.
* To test and validate the proposed web-application.
## Research Questions
1. What are the current channels that the public is using to report poorly disposed solid 
waste?
2. What are the major challenges faced by residents when using existing channels to report 
solid waste disposal issues in Nairobi?
3. How have the existing technologies influenced the participation of the public in solid 
waste management?
4. What functionalities and features should the web application possess to effectively 
support users in reporting poorly disposed waste within Nairobi?
5. How was the usability and effectiveness of the developed web application for waste 
reporting tested and validated
# Functional Requirements

## 1. User Authentication and Authorization
- Users must be able to create accounts, log in, and log out.
- Roles (User, Rewards Manager, Administrator) must be defined with specific permissions.
- Only authorized users should be able to perform certain actions based on their roles.

## 2. User Actions
- Users should be able to:
  - Claim and unclaim rewards.
  - View their claimed, awarded, eligible, and all rewards.
  - Earn points for specific activities (posting reports, meaningful comments).

## 3. Rewards Manager Actions
- Rewards Managers (and Administrators) should be able to:
  - Claim and unclaim rewards on behalf of users (in rare cases).
  - Award claimed rewards to users.
  - Add, edit, and delete reward categories (in rare cases).
  - Add, edit, and delete rewards (in rare cases).
  - View claimed, awarded, eligible, and all rewards for all users.

## 4. Administrator Actions
- Administrators should be able to perform all actions that Rewards Managers and Users can.
- Assign and unassign users as Reward Managers.

## 5. Reward Management
- Rewards should have:
  - Names and points required for redemption.
  - Categories.
- Rewards should be claimable, awarded, and unclaimed.

## 6. Point System
- Users should accumulate points based on specific actions (posting reports, meaningful comments).
- Points should be deducted when users claim rewards and refunded if they unclaim rewards.

## 7. User Interface
- The system should provide a user-friendly interface for users, Rewards Managers, and Administrators to interact with.
- It should display eligible rewards and reward-related information.

## 8. Data Management
- User, Reward, and User_Reward tables should be created and maintained.
- Data should be stored securely, including user credentials.

## 9. Error Handling
- The system should handle errors gracefully and provide informative error messages to users when needed.
- Error handling should be in place for scenarios like insufficient points, unauthorized actions, or database errors.

## 10. Database Queries
- The system should perform efficient database queries to retrieve reward-related information, user points, and more as required.

## 11. Data Cleanup
- Unclaimed rewards older than 30 days should be automatically deleted.

## 12. Security and Validation
- Input validation and security measures should be in place to prevent malicious actions, such as SQL injection or unauthorized access.

## 13. Logging and Auditing
- Log user actions and system events for auditing and debugging purposes.

## 14. Notifications
- Implement notifications to inform users about reward status changes, such as reward claims or point deductions.

# Non-Functional Requirements

## 15. Scalability and Performance
- Design the system to handle a growing number of users and rewards while maintaining good performance.

## 16. Documentation
- Provide user documentation for how to use the system.
- Document the system's architecture, database schema, and API (if applicable).

# Module Flowchart
```txt
1. User logs in
    |
    V
2. Eligible rewards are displayed for the user to see
    |
    V
3. User can choose to:
    |
    |---[User posts an approved report]---> Earn some points
    |
    |---[User comments meaningfully]------> Earn some points
    |
    |---[User selects a reward to claim]--> Points deducted
    |                                       and reward claimed
    |
    |---[User unclaims a reward]----------> Points refunded
    |
    V
4. User logs out
```
# Pseudocode

```python
# User logs in
if user_authenticated:
    user_id = get_user_id()
    eligible_rewards = calculate_eligible_rewards(user_id)
    display_rewards(eligible_rewards)

    if user_posts_approved_report():
        earn_points(user_id, points_for_report)

    if user_comments_meaningfully():
        earn_points(user_id, points_for_comment)

    if user_selects_reward_to_claim():
        reward_id = get_selected_reward_id()
        if deduct_points(user_id, reward_points):
            administrator_award_reward(user_id, reward_id)

    if user_unclaims_reward():
        reward_id = get_unclaimed_reward_id()
        if refund_points(user_id, reward_points):
            remove_unclaimed_reward(user_id, reward_id)

# User logs out
logout_user()
```

# Required Queries
## User-Related Queries

1. **Create User:**
   - SQL query to insert a new user record into the "User" table when a user registers.

2. **User Authentication:**
   - SQL query to verify user credentials (username/password) during login.

3. **Get User Information:**
   - Retrieve user details (e.g., name, points acquired, rewards claimed) based on user ID.

4. **Get User Role:**
   - Retrieve the role assigned to a user based on their user ID.

5. **Update User Profile:**
   - SQL query to update user information (e.g., profile picture, contact information).

6. **Assign Role to User:**
   - SQL query to assign a specific role to a user, typically performed by administrators.

## Reward-Related Queries

7. **Create Reward Category:**
   - Insert a new reward category into the "Reward" table.

8. **Create Reward:**
   - SQL query to add a new reward to the "Reward" table.

9. **Edit Reward:**
   - Update the details of an existing reward in the "Reward" table.

10. **Delete Reward:**
    - Remove a reward from the "Reward" table.

11. **Get All Rewards:**
    - Retrieve a list of all available rewards, including their details and point requirements.

12. **Get Reward by ID:**
    - Fetch a specific reward's details based on its ID.

## User Reward-Related Queries

13. **Claim Reward:**
    - Insert a new record into the "User_Reward" table when a user claims a reward.

14. **Unclaim Reward:**
    - Update the "User_Reward" table to unclaim a reward (or delete the record after 30 days).

15. **Get User's Claimed Rewards:**
    - Retrieve a list of rewards claimed by a specific user.

16. **Get User's Awarded Rewards:**
    - Fetch a list of rewards awarded to a specific user.

17. **Get User's Eligible Rewards:**
    - Determine which rewards are currently eligible for a specific user based on their points.

18. **Get All User Rewards:**
    - Retrieve a list of all user rewards, including claimed and awarded rewards for all users (for administrators).

19. **Award Reward:**
    - Update the "User_Reward" table to mark a reward as awarded (typically performed by administrators).

## Administrator-Related Queries

20. **Assign Reward Manager:**
    - Update user roles to assign a user as a reward manager.

21. **Unassign Reward Manager:**
    - Revoke the reward manager role from a user.

## General Queries

22. **Calculate User's Points:**
    - Calculate the total points acquired by a user based on their activities.

23. **Delete Expired Unclaimed Rewards:**
    - Periodically delete records of unclaimed rewards older than 30 days.

24. **Log User Actions:**
    - Insert log entries for various user actions and system events for auditing and debugging.
