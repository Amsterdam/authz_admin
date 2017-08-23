#!/usr/bin/env bash

cd $(dirname "$0")
cp -af oauth2/authz_admin_service/openapi-${DATAPUNT_ENVIRONMENT}.json \
      swagger-ui/dist/openapi.json &&
  authz_admin_service
