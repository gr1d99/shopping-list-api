from main import bcrypt, db


class BaseModel(db.Model):
    """
    Base class for all models.
    Contains common methods used by all models.
    """
    __abstract__ = True

    def save(self):
        # check if username exists before actually saving the data
        self.check_username(self.username)
        return self._save()

    def _save(self):
        db.session.add(self)
        db.session.commit()


class BaseUserManager(object):
    @classmethod
    def hash_password(cls, raw_password):
        """
        never store passwords in plaintext, this method
        hashes the raw password and returns hashed password.
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

    def _verify_password(self, raw_password):
        """
        used to verify user password using the provided raw_password
        since password stored are hashed.
        """
        return bcrypt.check_password_hash(self.password, raw_password)
