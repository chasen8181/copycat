{{- define "copycat.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "copycat.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "copycat.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "copycat.labels" -}}
helm.sh/chart: {{ include "copycat.chart" . }}
{{ include "copycat.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "copycat.selectorLabels" -}}
app.kubernetes.io/name: {{ include "copycat.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "copycat.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "copycat.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "copycat.authSecretName" -}}
{{- if .Values.auth.existingSecret -}}
{{- .Values.auth.existingSecret -}}
{{- else -}}
{{- printf "%s-auth" (include "copycat.fullname" .) -}}
{{- end -}}
{{- end -}}

{{- define "copycat.controllerType" -}}
{{- default "Deployment" .Values.controller.type -}}
{{- end -}}

{{- define "copycat.headlessServiceName" -}}
{{- printf "%s-headless" (include "copycat.fullname" .) -}}
{{- end -}}

{{- define "copycat.useVolumeClaimTemplate" -}}
{{- if and (eq (include "copycat.controllerType" .) "StatefulSet") .Values.persistence.enabled (not .Values.persistence.existingClaim) .Values.persistence.volumeClaimTemplate.enabled -}}true{{- else -}}false{{- end -}}
{{- end -}}

{{- define "copycat.persistentVolumeClaimName" -}}
{{- default (include "copycat.fullname" .) .Values.persistence.existingClaim -}}
{{- end -}}

{{- define "copycat.probePath" -}}
{{- if .Values.pathPrefix -}}
{{- printf "%s/health" .Values.pathPrefix -}}
{{- else -}}
/health
{{- end -}}
{{- end -}}
