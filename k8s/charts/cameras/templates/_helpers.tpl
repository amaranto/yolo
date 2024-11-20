{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cameras.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cameras.labels" -}}
helm.sh/chart: {{ include "cameras.chart" . }}
{{ include "cameras.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cameras.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cameras.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
cameras chart 
*/}}
{{- define "cameras.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
cameras name 
*/}}
{{- define "cameras.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Vault credentials template
*/}}
{{- define "vault.credentials" -}}
{{- printf `{{- with secret "%s" -}}
{
  "username": "{{ .Data.data.username }}",
  "password": "{{ .Data.data.password }}"
}
{{- end }}` . -}}
{{- end }}

{{/*
Vault keys template
*/}}
{{- define "vault.keys" -}}
{{- printf `{{- with secret "%s" -}}
{
  "private_key": "{{ .Data.data.private_key }}",
  "public_key": "{{ .Data.data.public_key }}",
  "address": "{{ .Data.data.address }}"
}
{{- end }}` . -}}
{{- end }}