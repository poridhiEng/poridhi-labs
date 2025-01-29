# Linux User and Group Management

In this lab, we will explore how to manage users and groups in a Linux environment. By the end of this lab, you will be able to:

- Create user accounts.
- Create and manage groups.
- Assign users to primary and supplementary groups.
- Lock and verify user accounts.

These tasks are essential for system administrators to efficiently manage user access and permissions. 

## Understanding Key Concepts

### 1. Superuser

A **superuser** is a user account with administrative privileges, typically the `root` user in Linux. Superusers can create, modify, and delete users and groups, as well as perform system-wide changes. To execute administrative tasks, we use the `sudo` command, which allows permitted users to run commands as a superuser.

### 2. Primary and Supplementary Groups
- A **primary group** is the default group assigned to a user when they create new files. Each user must have a primary group.
- **Supplementary groups** provide additional permissions and access to resources. A user can belong to multiple supplementary groups, which help in fine-grained access control.

### 3. Locking a User Account
Locking a user account prevents the user from logging in without deleting their data or removing their access permanently. This is useful for temporarily restricting access.

---

## Lab Tasks

### 1. Adding Users to the System

**Objective:** Create user accounts for employees of Poridhi Company.

**Command:**
```bash
sudo useradd <username>
```

**Explanation:**
- The `useradd` command creates a new user.
- By default, a home directory is assigned unless specified otherwise.
- The system applies default configurations like shell and group settings.

**Steps:** Add the following users:
- `nabil`
- `minhaz`
- `yasin`
- `fazlul`

**Commands:**
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
Example output:
```
uid=1001(nabil) gid=1001(nabil) groups=1001(nabil)
```

---

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
Example output:
```
poridhi-minions:x:1002:
```

---

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
Example output:
```
uid=1001(nabil) gid=1002(poridhi-minions) groups=1002(poridhi-minions)
```

---

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
Example output:
```
uid=1002(minhaz) gid=1002(minhaz) groups=1002(minhaz),1002(poridhi-minions)
```

---

### 5. Locking a User Account

**Objective:** Temporarily disable the user account of `fazlul`.

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
Example output:
```
fazlul L 2024-01-28 0 99999 7 -1 (Password locked)
```

---

## Verification Commands

Use the following commands to confirm user and group settings:

1. **Check User Information:**
   ```bash
   id <username>
   ```
   Example:
   ```bash
   id nabil
   ```

2. **Check Group Membership:**
   ```bash
   getent group poridhi-minions
   ```
   Example output:
   ```
   poridhi-minions:x:1002:nabil,minhaz,yasin,fazlul
   ```

3. **Check Account Status:**
   ```bash
   passwd -S <username>
   ```
   Example:
   ```bash
   passwd -S fazlul
   ```

---

## Conclusion

In this lab, we covered essential user and group management tasks for **Poridhi Company**. You have learned how to:

- Add users to the system.
- Create and manage groups.
- Assign primary and supplementary groups.
- Lock user accounts.

These skills are crucial for managing user access and security in a Linux system. Practice these commands further to reinforce your understanding. With these tools, Poridhi Company can efficiently handle user management and access control!

