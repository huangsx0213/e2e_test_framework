# Templates Usage Guide

This guide provides detailed variable filling rules for the `create_customer.xml` and `create_user.json` templates.

## Variable Filling Rules

The templates use Jinja syntax (`{{ variable }}`) to denote placeholders that will be dynamically replaced with actual data during the test execution. The variables correspond to the structure and hierarchy of the default values provided in the JSON configuration (`body_defaults`).

---

## 1. `create_customer.xml`

### Variable Definitions

- **`{{ name }}`**: The name of the customer.
  - Corresponds to `name` in the body default JSON.

- **`{{ contact.name }}`**: The name of the contact person.
  - Corresponds to `contact.name` in the body default JSON.

- **`{{ contact.email }}`**: The email address of the contact person.
  - Corresponds to `contact.email` in the body default JSON.

- **`{{ address.street }}`**: The street address of the customer.
  - Corresponds to `address.street` in the body default JSON.

- **`{{ address.city }}`**: The city of the customer.
  - Corresponds to `address.city` in the body default JSON.

- **`{{ address.zipcode }}`**: The zipcode of the customer.
  - Corresponds to `address.zipcode` in the body default JSON.

---

## 2. `create_user.json`

### Variable Definitions

- **`{{ name }}`**: The name of the user.
  - Corresponds to `name` in the body default JSON.

- **`{{ email }}`**: The email address of the user.
  - Corresponds to `email` in the body default JSON.

- **`{{ address.street }}`**: The street address of the user.
  - Corresponds to `address.street` in the body default JSON.

- **`{{ address.city }}`**: The city of the user.
  - Corresponds to `address.city` in the body default JSON.

- **`{{ address.state }}`**: The state of the user.
  - Corresponds to `address.state` in the body default JSON.

- **`{{ address.zip }}`**: The zip code of the user.
  - Corresponds to `address.zip` in the body default JSON.

### Loop and Filter Functions

- **`{% for phone in phones %}...{% endfor %}`**: Loop through each phone entry in the `phones` array. Each phone entry will have its type and number dynamically replaced.
  - Corresponds to each phone item in the `phones` array in the body default JSON.

- **`{{ phone.type }}`**: The type of the phone (e.g., home, work).
  - Corresponds to `phones[].type` in the body default JSON.

- **`{{ phone.number }}`**: The phone number.
  - Corresponds to `phones[].number` in the body default JSON.

- **`{{ preferences.newsletter | json_bool }}`**: Whether the user prefers newsletters. The custom filter `json_bool` converts Python boolean values to JSON boolean values.
  - Corresponds to `preferences.newsletter` in the body default JSON.

- **`{{ preferences.notifications.email | json_bool }}`**: Whether the user prefers email notifications. The custom filter `json_bool` converts Python boolean values to JSON boolean values.
  - Corresponds to `preferences.notifications.email` in the body default JSON.

- **`{{ preferences.notifications.sms | json_bool }}`**: Whether the user prefers SMS notifications. The custom filter `json_bool` converts Python boolean values to JSON boolean values.
  - Corresponds to `preferences.notifications.sms` in the body default JSON.