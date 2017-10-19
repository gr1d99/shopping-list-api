
from main import bcrypt, db
from web_app.core.exceptions import EmailExists, UsernameExists


class BaseModel(db.Model):
    """
    Base class for all models.
    Contains common methods used by all models.
    """
    __abstract__ = True

    # ----Attach to class-------- #
    # we will never have to import
    # these exceptions to where
    # User class has been imported
    UsernameExists = UsernameExists
    EmailExists = EmailExists
    # --------------------------- #

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    def save(self):
        return self._save()

    def _save(self):
        db.session.add(self)
        db.session.commit()


class BaseUserManager(object):
    def authenticate(self):
        self.authenticated = True
        self.save()
        return True

    def deauthenticate(self):
        self.authenticated = False
        self.save()
        return True

    @property
    def is_authenticated(self):
        return self.authenticated

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

    def validate_required(self):
        """
        A method to inspect required columns.

        Passing an empty string passes non-nullable flag,
        this method helps handle that flaw.
        Field names are included in the error message to
        assist in debugging.
        """
        error_message = '%(col)s is required'
        errors = {}
        for col in self.REQUIRED_COLUMNS:
            if getattr(self, col) == '':
                errors.update({col: error_message % dict(col=col)})

        if errors is not {}:
            return errors

        else:
            return None

    def verify_password(self, password):
        return self._verify_password(password)

    # bcrypt saves us the work of checking password column.
    # we only need to add critical columns to REQUIRED_COLUMNS.

    # NB. This allows addition of other colums which appear in the Model.
    # passing a column which does not exist will raise AttributeError.
    REQUIRED_COLUMNS = ['username', 'email']
