# Linux User and Group Management

Managing users and groups is a fundamental aspect of Linux system administration. This lab will guide you through creating user accounts, managing groups, assigning users to groups, and locking user accounts. These tasks are crucial for effectively controlling user access and permissions.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/0e3dffef046890d0870a9be043d4be57e5a7026b/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/Linux-user.svg)

By the end of this lab, you will be able to:
- Create user accounts.
- Create and manage groups.
- Assign users to primary and supplementary groups.
- Lock and verify user accounts. 
- Unlock user accounts.
- List all users.

## Understanding Key Concepts

### Primary Group

The primary group is the **default group** assigned to a user when they create files or directories.

- Every user must belong to **exactly one primary group**.
- By default, when creating a user, the system creates a group with the **same name as the username** and assigns it as the primary group.


### Supplementary Groups

Supplementary groups are additional groups a user belongs to, **granting extra permissions beyond their primary group**.

- A user can belong to **multiple supplementary groups**.
- These are stored in `/etc/group`.

#### Example Scenario:

Imagine a company where employees belong to different departments. When a new software developer joins, they are assigned to the `Developers` group as their primary group. However, they also need access to project documentation, so they are added to the `Docs` group as a supplementary group.

### Locking a User Account

Locking a user account prevents the user from logging in without deleting their data or removing their access permanently. This is useful for temporarily restricting access.

#### Example Scenario:

A system administrator needs to temporarily disable access for an employee who is on a long vacation. Instead of deleting their account, the admin locks it so that they cannot log in until they return.

## Lab Tasks

We will understand the whole process of creating users and groups using the example of `Poridhi` where we will create 4 users and 1 group.

### 1. Adding Users to the System

**Objective:** Create user accounts for employees of `Poridhi`.

**Command:**

```bash
sudo useradd <username>
```

**Explanation:**
- The `useradd` command creates a new user.
- By default, a home directory is assigned unless specified otherwise.
- The primary group is the same as the username by default.

Now we will create 4 users `nabil`, `minhaz`, `yasin`, and `fazlul`.

```bash
sudo useradd nabil
sudo useradd minhaz
sudo useradd yasin
sudo useradd fazlul
```

**Verification:**

```bash
id nabil
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image.png)

The output shows that `nabil` has:  

- **UID 1000** (User ID) and **GID 1000** (Group ID), meaning they belong to a primary group named `nabil`.  
- No supplementary groups, so they only have access to resources assigned to their primary group.  

### 2. Creating the `Poridhi-Minions` Group

**Objective:** Create a group for administrative users.

**Command:**
```bash
sudo groupadd poridhi-minions
```

**Explanation:**
- The `groupadd` command creates a new group.
- Groups allow multiple users to share permissions efficiently.

**Verification:**
```bash
getent group poridhi-minions
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-1.png)

This output shows that the group **`poridhi-minions`** exists with:  

- **GID 1004** (Group ID).  
- No users listed, meaning no one is currently a member of this group.  

### 3. Assigning a Primary Group to a User

**Objective:** Set `poridhi-minions` as the primary group for `nabil`.

**Command:**
```bash
sudo usermod -g poridhi-minions nabil
```

**Explanation:**
- The `usermod` command modifies user settings.
- The `-g` option changes the primary group.

**Verification:**
```bash
id nabil
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-2.png)

This output shows that:  

- **`nabil`** has **UID 1000** (User ID).  
- **Primary group** is now **`poridhi-minions`** with **GID 1004**.  
- **Belongs only** to the **`poridhi-minions`** group (no supplementary groups).  

We can also verify the group of nabil by:

```bash
groups nabil
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-3.png)

### 4. Adding Users to a Supplementary Group

**Objective:** Add `minhaz`, `yasin`, and `fazlul` to `poridhi-minions` as a supplementary group.


**Command:**
```bash
sudo usermod -aG poridhi-minions <username>
```

**Explanation:**
- The `-aG` option appends a user to a supplementary group without removing them from existing groups.
- Users in supplementary groups gain additional access privileges.

**Commands:**
```bash
sudo usermod -aG poridhi-minions minhaz
sudo usermod -aG poridhi-minions yasin
sudo usermod -aG poridhi-minions fazlul
```

**Verification:**
```bash
id minhaz
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-4.png)

The output shows the user `minhaz` and their group memberships:  

- **`uid=1001(minhaz)`** → `minhaz` has a user ID (UID) of `1001`.  
- **`gid=1001(minhaz)`** → `minhaz`'s **primary group** is `1001(minhaz)`.  
- **`groups=1001(minhaz),1004(poridhi-minions)`** → `minhaz` is also a **supplementary member** of the `poridhi-minions` group (GID `1004`).  

We can also verify the group of minhaz by:

```bash
groups minhaz
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-5.png)

We can also check the members of the group `poridhi-minions` by:

```bash
getent group poridhi-minions
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-6.png)

This output shows that:  

- **Group name:** `poridhi-minions`  
- **GID (Group ID):** `1004`  
- **Members:** `minhaz`, `yasin`, `fazlul` (they are part of this supplementary group)  

**Note:** `nabil` is not listed as a member of `poridhi-minions` because `nabil`'s primary group is set to `poridhi-minions` (GID `1004`), rather than being added as a **supplementary group member**.


### 5. Locking a User Account

**Objective:** Suppose fazlul is on a long vacation and we need to temporarily disable the user account of `fazlul` so that he cannot log in to the system.

**Command:**
```bash
sudo usermod -L fazlul
```

**Explanation:**
- The `-L` option locks an account, preventing password-based login.
- The user’s data remains intact.

**Verification:**
```bash
passwd -S fazlul
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-7.png)

The output of `passwd -S fazlul` provides the status of the user account `fazlul`:

- **`L`** → The account is **locked**, meaning the user cannot log in.  
- **`02/10/2025`** → Last password change date.  
- **`0`** → Minimum days before the password can be changed (0 means no restriction).  
- **`99999`** → Maximum days before the password expires (99999 means never expires).  
- **`7`** → Warning period (days before expiration to notify the user).  
- **`-1`** → Password inactivity period (-1 means no automatic account deactivation).

### 6. Unlocking a User Account

**Objective:** After fazlul's vacation, we need to unlock his account so that he can log in to the system again.

**Command:**
```bash
sudo usermod -U fazlul
```

**Explanation:**
- The `-U` option unlocks an account.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-8.png)

Oops! Seems like we have encountered an error. This error occurs because the user account `fazlul` does **not have a password set**, and unlocking it with `usermod -U` would leave the account passwordless (a security risk). To resolve this, you need to **set a password** for the user first.

**Set a password first:**

```bash
sudo passwd fazlul
```

**Then unlock the account:**

```bash
sudo usermod -U fazlul
```

**Verification:**


```bash 
passwd -S fazlul
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-9.png)

The command `passwd -S fazlul` shows the status of the user `fazlul`'s password.  

- **`P`** → The account has a **usable password** (unlocked).  
- **`02/10/2025`** → Date of the last password change.  
- **`0`** → Minimum days required before changing the password (0 = can change anytime).  
- **`99999`** → Maximum days before the password expires (99999 = password never expires).  
- **`7`** → Number of days before expiration to warn the user.  
- **`-1`** → Account is not set to expire.  

This means `fazlul`'s account is now **active** with a password set.

### 7. List All Users

To see all users present in a Linux system, you can check the `/etc/passwd` file, which contains user account information.

```bash
cat /etc/passwd
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Linux%20Labs/Lab%2002/images/image-10.png)

## Conclusion

Effective user and group management is essential for maintaining security and organization in a Linux system. Through this lab, you have learned how to create user accounts, manage groups, and control access by assigning users to primary and supplementary groups. Additionally, you explored how to lock user accounts when necessary to ensure better security control and unlock them when necessary.
