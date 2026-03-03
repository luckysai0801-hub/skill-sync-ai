/**
 * services/api.js – Axios client for SkillSync AI backend.
 */
import axios from 'axios'

const API = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    headers: { 'Content-Type': 'application/json' },
    timeout: 60000,
    withCredentials: true,
})

// ─── Response interceptor ────────────────────────────────────────────────────
// On 401: clear stored token and redirect to login (token is expired/invalid)
API.interceptors.response.use(
    response => response,
    error => {
        if (
            error.response?.status === 401 &&
            !error.config?.url?.includes('/auth/') // don't redirect on auth endpoint failures
        ) {
            // Token is invalid — clear it and send user to login
            localStorage.removeItem('skillsync_token')
            delete API.defaults.headers.common['Authorization']
            if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

// ──────────────────────────────────────────────
// Resume Endpoints
// ──────────────────────────────────────────────

export const uploadResume = async (userId, file) => {
    const form = new FormData()
    form.append('user_id', userId)
    form.append('file', file)
    const { data } = await API.post('/resume/upload-resume', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
}

export const getResumeScore = async (candidateId) => {
    const { data } = await API.get(`/resume/resume-score/${candidateId}`)
    return data
}

export const getResume = async (resumeId) => {
    const { data } = await API.get(`/resume/${resumeId}`)
    return data
}

// ──────────────────────────────────────────────
// Job Endpoints
// ──────────────────────────────────────────────

export const createJob = async (payload) => {
    const { data } = await API.post('/job/create-job', payload)
    return data
}

export const listJobs = async () => {
    const { data } = await API.get('/job/jobs')
    return data
}

export const getJob = async (jobId) => {
    const { data } = await API.get(`/job/jobs/${jobId}`)
    return data
}

// ──────────────────────────────────────────────
// Matching Endpoints
// ──────────────────────────────────────────────

export const matchJobs = async (candidateId) => {
    const { data } = await API.get(`/match-jobs/${candidateId}`)
    return data
}

export const matchCandidates = async (jobId) => {
    const { data } = await API.get(`/match-candidates/${jobId}`)
    return data
}

export const getSkillGap = async (candidateId, jobId) => {
    const { data } = await API.get(`/skill-gap/${candidateId}/${jobId}`)
    return data
}

export const getInterviewProbability = async (candidateId, jobId) => {
    const { data } = await API.get(`/interview-probability/${candidateId}/${jobId}`)
    return data
}

export const getRecruiterDashboard = async (jobId) => {
    const { data } = await API.get(`/recruiter-dashboard/${jobId}`)
    return data
}

export default API
