# Django Admin Guide for Expert Verification

## Overview

The Django admin interface provides comprehensive tools for managing expert verification, user profiles, and consultation requests in the FarmSmart platform.

## Accessing Django Admin

### 1. Create Superuser

```bash
# Option 1: Use Django command
python manage.py createsuperuser

# Option 2: Use the provided script
python create_admin.py
```

### 2. Access Admin Interface

- URL: `http://127.0.0.1:8000/admin/`
- Login with superuser credentials

## Admin Features

### 1. User Profiles Management

#### Location: `Admin > User Profiles`

**List View Features:**

- **User Info**: Clickable user name linking to user details
- **Account Type**: Expert or Customer
- **Specialization**: Expert's area of expertise
- **Experience**: Years of experience
- **Verification Status**: Visual status indicators
- **Location**: User's location
- **Created Date**: Registration date

**Filtering Options:**

- Account Type (Expert/Customer)
- Verification Status (Verified/Pending)
- Creation Date
- Experience Years

**Search Capabilities:**

- Username, email, first name, last name
- Specialization
- Location
- Certification

### 2. Expert Verification Process

#### Step-by-Step Verification:

1. **Navigate to User Profiles**

   - Go to `Admin > User Profiles`
   - Filter by "Account Type: Expert"

2. **Review Expert Information**

   - Click on expert's name to view full profile
   - Check specialization, experience, certifications
   - Review bio and contact information

3. **Review Documents**

   - Check "Verification Documents" section
   - Click document links to view uploaded files
   - Verify certificate of practice
   - Verify ID document

4. **Verify Expert**
   - Check "is_verified" checkbox
   - Add verification notes if needed
   - Save changes

#### Bulk Verification Actions:

1. **Select Multiple Experts**

   - Use checkboxes to select experts
   - Use filters to narrow down selection

2. **Choose Action**

   - "Verify selected experts" - Marks as verified
   - "Unverify selected experts" - Removes verification
   - "Export expert list" - Exports expert data

3. **Execute Action**
   - Click "Go" button
   - Confirm action

### 3. Document Management

#### Document Types:

- **Certificate of Practice**: Professional certification
- **ID Document**: Government-issued identification

#### Document Actions:

- **View**: Click document links to open in new tab
- **Download**: Right-click and save document
- **Verify**: Check document authenticity
- **Note**: Add verification notes

### 4. User Management

#### Location: `Admin > Users`

**Enhanced User List:**

- Account Type column
- Verification Status column
- Profile information inline

**User Profile Inline:**

- Edit profile directly from user page
- All profile fields accessible
- Verification controls
- Document management

### 5. Consultation Management

#### Location: `Admin > Expert Consultations`

**List View:**

- Subject, Customer, Expert
- Status with color coding
- Creation and update dates

**Status Management:**

- Pending: New consultation request
- Accepted: Expert accepted request
- In Progress: Consultation ongoing
- Completed: Consultation finished
- Cancelled: Request cancelled

**Bulk Actions:**

- Mark as pending
- Mark as accepted
- Mark as completed
- Mark as cancelled

## Admin Interface Layout

### Main Navigation

```
Django Administration
├── Users
│   ├── Users (with profile inline)
│   └── User profiles
├── Main
│   ├── Community posts
│   ├── Crop recommendations
│   ├── Expert consultations
│   └── Farm data
└── Authentication and Authorization
    ├── Groups
    └── Users
```

### User Profiles Admin Layout

```
User Profiles
├── List View
│   ├── User Info (linked)
│   ├── Account Type
│   ├── Specialization
│   ├── Experience
│   ├── Verification Status
│   ├── Location
│   └── Created Date
├── Filters
│   ├── Account Type
│   ├── Verification Status
│   ├── Created Date
│   └── Experience Years
├── Search
│   ├── User fields
│   ├── Profile fields
│   └── Specialization
└── Actions
    ├── Verify experts
    ├── Unverify experts
    └── Export expert list
```

## Verification Workflow

### 1. Expert Registration

1. Expert registers with account type "Expert"
2. Expert uploads verification documents
3. Expert completes profile information
4. System creates UserProfile with `is_verified=False`

### 2. Admin Review

1. Admin receives notification of new expert
2. Admin reviews expert profile
3. Admin checks uploaded documents
4. Admin verifies document authenticity

### 3. Verification Decision

1. **Approve**: Check `is_verified=True`
2. **Reject**: Add verification notes, keep `is_verified=False`
3. **Request More Info**: Add notes, contact expert

### 4. Post-Verification

1. Verified experts appear in expert list
2. Farmers can request consultations
3. Expert receives verification notification

## Best Practices

### 1. Verification Process

- Always review documents thoroughly
- Check specialization matches experience
- Verify contact information
- Add detailed verification notes

### 2. Document Security

- Never share document URLs publicly
- Use admin interface for document access
- Maintain verification audit trail
- Respect privacy regulations

### 3. User Management

- Regularly review expert profiles
- Update verification status as needed
- Monitor consultation quality
- Handle user complaints promptly

### 4. System Maintenance

- Regular backup of admin data
- Monitor system performance
- Update admin configurations
- Train admin users properly

## Troubleshooting

### Common Issues:

1. **Profile Not Found**

   - Check if UserProfile exists
   - Create profile if missing
   - Link to correct user

2. **Document Access Issues**

   - Check file permissions
   - Verify media settings
   - Check file paths

3. **Verification Not Updating**

   - Clear browser cache
   - Check database constraints
   - Verify admin permissions

4. **Bulk Actions Not Working**
   - Check action permissions
   - Verify queryset selection
   - Review action implementation

## Security Considerations

### 1. Access Control

- Limit admin access to trusted users
- Use strong passwords
- Enable two-factor authentication
- Regular access reviews

### 2. Data Protection

- Secure document storage
- Encrypt sensitive data
- Regular security updates
- Monitor access logs

### 3. Privacy Compliance

- Follow data protection regulations
- Secure document handling
- User consent management
- Data retention policies

## Support

For technical support or questions about the admin interface:

- Check Django admin documentation
- Review model configurations
- Test in development environment
- Contact system administrator
