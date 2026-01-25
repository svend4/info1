#!/usr/bin/env python3
"""
SSO/SAML Integration

Интеграция с enterprise SSO провайдерами (Okta, Azure AD, Google Workspace).
"""

import base64
import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from xml.etree import ElementTree as ET


class SSOProvider(Enum):
    """SSO Provider Types"""
    OKTA = "okta"
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    ONELOGIN = "onelogin"
    PING_IDENTITY = "ping_identity"
    CUSTOM_SAML = "custom_saml"


class SAMLBindingType(Enum):
    """SAML Binding Types"""
    HTTP_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTP_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    HTTP_ARTIFACT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"


@dataclass
class SSOConfig:
    """SSO Configuration"""
    provider: SSOProvider
    entity_id: str  # Service Provider Entity ID
    sso_url: str  # Identity Provider SSO URL
    slo_url: Optional[str]  # Single Logout URL
    x509_cert: str  # IDP Certificate
    sp_private_key: Optional[str]  # Service Provider Private Key
    binding: SAMLBindingType = SAMLBindingType.HTTP_POST
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    sign_requests: bool = True
    encrypt_assertions: bool = True
    attribute_mapping: Dict[str, str] = None

    def __post_init__(self):
        if self.attribute_mapping is None:
            self.attribute_mapping = {
                'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                'first_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
                'last_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
                'roles': 'http://schemas.xmlsoap.org/claims/Group'
            }


@dataclass
class SAMLRequest:
    """SAML Authentication Request"""
    id: str
    issue_instant: datetime
    destination: str
    assertion_consumer_service_url: str
    issuer: str
    name_id_format: str

    def to_xml(self) -> str:
        """Generate SAML AuthnRequest XML"""
        request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                     xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                     ID="{self.id}"
                     Version="2.0"
                     IssueInstant="{self.issue_instant.strftime('%Y-%m-%dT%H:%M:%SZ')}"
                     Destination="{self.destination}"
                     AssertionConsumerServiceURL="{self.assertion_consumer_service_url}"
                     ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{self.issuer}</saml:Issuer>
    <samlp:NameIDPolicy Format="{self.name_id_format}" AllowCreate="true"/>
</samlp:AuthnRequest>"""
        return request


@dataclass
class SAMLResponse:
    """SAML Authentication Response"""
    name_id: str
    session_index: str
    attributes: Dict[str, Any]
    issuer: str
    audience: str
    not_before: datetime
    not_on_or_after: datetime
    authn_instant: datetime


@dataclass
class SSOSession:
    """SSO User Session"""
    session_id: str
    user_id: str
    email: str
    name_id: str
    session_index: str
    provider: SSOProvider
    attributes: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    is_active: bool = True


class SSOIntegration:
    """SSO/SAML Integration Manager"""

    def __init__(self, config: SSOConfig):
        """
        Инициализация SSO интеграции

        Args:
            config: SSO configuration
        """
        self.config = config
        self.sessions: Dict[str, SSOSession] = {}
        self._metadata_cache: Optional[str] = None

    def get_login_url(self, return_url: str) -> str:
        """
        Генерация URL для SAML login redirect

        Args:
            return_url: URL для возврата после авторизации

        Returns:
            SAML login redirect URL
        """
        request = SAMLRequest(
            id=f"_saml_{uuid.uuid4().hex}",
            issue_instant=datetime.utcnow(),
            destination=self.config.sso_url,
            assertion_consumer_service_url=return_url,
            issuer=self.config.entity_id,
            name_id_format=self.config.name_id_format
        )

        # Generate XML
        saml_request_xml = request.to_xml()

        # Base64 encode
        encoded_request = base64.b64encode(saml_request_xml.encode()).decode()

        # Build redirect URL
        if self.config.binding == SAMLBindingType.HTTP_REDIRECT:
            redirect_url = f"{self.config.sso_url}?SAMLRequest={encoded_request}"
            if self.config.sign_requests:
                # Add signature parameters
                redirect_url += f"&SigAlg=http://www.w3.org/2001/04/xmldsig-more%23rsa-sha256"
        else:
            # HTTP-POST binding - return form submission URL
            redirect_url = self.config.sso_url

        return redirect_url

    def process_saml_response(self, saml_response_b64: str) -> SAMLResponse:
        """
        Обработка SAML response от IDP

        Args:
            saml_response_b64: Base64-encoded SAML response

        Returns:
            Parsed SAML response

        Raises:
            ValueError: If response is invalid
        """
        # Decode base64
        saml_xml = base64.b64decode(saml_response_b64).decode()

        # Parse XML
        root = ET.fromstring(saml_xml)

        # Extract namespaces
        ns = {
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'
        }

        # Verify signature (simplified - production should use cryptography library)
        if self.config.sign_requests:
            self._verify_signature(root, ns)

        # Extract assertion
        assertion = root.find('.//saml:Assertion', ns)
        if assertion is None:
            raise ValueError("No assertion found in SAML response")

        # Extract subject
        subject = assertion.find('.//saml:Subject', ns)
        name_id_elem = subject.find('.//saml:NameID', ns)
        name_id = name_id_elem.text if name_id_elem is not None else ""

        # Extract session index
        authn_statement = assertion.find('.//saml:AuthnStatement', ns)
        session_index = authn_statement.get('SessionIndex', '') if authn_statement is not None else ""

        # Extract attributes
        attributes = {}
        attr_statements = assertion.findall('.//saml:AttributeStatement/saml:Attribute', ns)
        for attr in attr_statements:
            attr_name = attr.get('Name', '')
            attr_values = [val.text for val in attr.findall('.//saml:AttributeValue', ns)]

            # Map to standard names
            mapped_name = self._map_attribute_name(attr_name)
            attributes[mapped_name] = attr_values[0] if len(attr_values) == 1 else attr_values

        # Extract conditions
        conditions = assertion.find('.//saml:Conditions', ns)
        not_before_str = conditions.get('NotBefore', '')
        not_on_or_after_str = conditions.get('NotOnOrAfter', '')

        not_before = datetime.fromisoformat(not_before_str.replace('Z', '+00:00')) if not_before_str else datetime.utcnow()
        not_on_or_after = datetime.fromisoformat(not_on_or_after_str.replace('Z', '+00:00')) if not_on_or_after_str else datetime.utcnow() + timedelta(hours=8)

        # Extract issuer and audience
        issuer_elem = assertion.find('.//saml:Issuer', ns)
        issuer = issuer_elem.text if issuer_elem is not None else ""

        audience_elem = assertion.find('.//saml:AudienceRestriction/saml:Audience', ns)
        audience = audience_elem.text if audience_elem is not None else ""

        authn_instant_str = authn_statement.get('AuthnInstant', '') if authn_statement is not None else ''
        authn_instant = datetime.fromisoformat(authn_instant_str.replace('Z', '+00:00')) if authn_instant_str else datetime.utcnow()

        return SAMLResponse(
            name_id=name_id,
            session_index=session_index,
            attributes=attributes,
            issuer=issuer,
            audience=audience,
            not_before=not_before,
            not_on_or_after=not_on_or_after,
            authn_instant=authn_instant
        )

    def create_session(self, saml_response: SAMLResponse, user_id: str) -> SSOSession:
        """
        Создание SSO сессии

        Args:
            saml_response: Parsed SAML response
            user_id: Internal user ID

        Returns:
            Created SSO session
        """
        session = SSOSession(
            session_id=f"sso_{uuid.uuid4().hex}",
            user_id=user_id,
            email=saml_response.attributes.get('email', ''),
            name_id=saml_response.name_id,
            session_index=saml_response.session_index,
            provider=self.config.provider,
            attributes=saml_response.attributes,
            created_at=datetime.utcnow(),
            expires_at=saml_response.not_on_or_after,
            is_active=True
        )

        self.sessions[session.session_id] = session
        return session

    def validate_session(self, session_id: str) -> Optional[SSOSession]:
        """
        Валидация SSO сессии

        Args:
            session_id: Session ID to validate

        Returns:
            Valid session or None
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check expiration
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            return None

        if not session.is_active:
            return None

        return session

    def logout(self, session_id: str) -> bool:
        """
        SSO logout (SLO - Single Logout)

        Args:
            session_id: Session to logout

        Returns:
            True if successful
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.is_active = False

        # If SLO URL is configured, send logout request to IDP
        if self.config.slo_url:
            logout_request = self._build_logout_request(session)
            # Send to IDP (implementation depends on binding type)
            # For now, just mark as inactive

        return True

    def get_sp_metadata(self) -> str:
        """
        Генерация Service Provider metadata XML

        Returns:
            SP metadata XML
        """
        if self._metadata_cache:
            return self._metadata_cache

        metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                      entityID="{self.config.entity_id}">
    <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
                         AuthnRequestsSigned="{str(self.config.sign_requests).lower()}"
                         WantAssertionsSigned="true">
        <md:NameIDFormat>{self.config.name_id_format}</md:NameIDFormat>
        <md:AssertionConsumerService Binding="{self.config.binding.value}"
                                      Location="{self.config.entity_id}/acs"
                                      index="0"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""

        self._metadata_cache = metadata
        return metadata

    def _verify_signature(self, xml_element: ET.Element, namespaces: Dict[str, str]):
        """
        Verify SAML response signature

        Args:
            xml_element: XML element to verify
            namespaces: XML namespaces

        Raises:
            ValueError: If signature is invalid
        """
        # Simplified signature verification
        # Production should use python-saml or pysaml2
        signature = xml_element.find('.//ds:Signature', {**namespaces, 'ds': 'http://www.w3.org/2000/09/xmldsig#'})
        if signature is None and self.config.sign_requests:
            raise ValueError("Missing required signature")

    def _map_attribute_name(self, saml_attribute: str) -> str:
        """
        Map SAML attribute to standard name

        Args:
            saml_attribute: SAML attribute name

        Returns:
            Mapped attribute name
        """
        for standard_name, saml_name in self.config.attribute_mapping.items():
            if saml_name == saml_attribute:
                return standard_name
        return saml_attribute

    def _build_logout_request(self, session: SSOSession) -> str:
        """
        Build SAML logout request

        Args:
            session: Session to logout

        Returns:
            SAML logout request XML
        """
        request_id = f"_logout_{uuid.uuid4().hex}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        logout_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                      xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                      ID="{request_id}"
                      Version="2.0"
                      IssueInstant="{issue_instant}"
                      Destination="{self.config.slo_url}">
    <saml:Issuer>{self.config.entity_id}</saml:Issuer>
    <saml:NameID Format="{self.config.name_id_format}">{session.name_id}</saml:NameID>
    <samlp:SessionIndex>{session.session_index}</samlp:SessionIndex>
</samlp:LogoutRequest>"""

        return logout_request
