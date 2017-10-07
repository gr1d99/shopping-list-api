from main import db, bcrypt


class BaseUser(db.Model):
    @classmethod
    def hash_password(cls, raw_password):
        """
        never store passwords in plaintext
        :param raw_password:
        :return: hashed password
        """
        return bcrypt.generate_password_hash(raw_password)

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email
