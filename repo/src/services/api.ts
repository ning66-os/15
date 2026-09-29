import axios from 'axios'
import type { MeetingNote, TasteScore, TissueEngineeringParams, AudioProcessingResult } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
})

export const meetingApi = {
  createMeeting: (data: Partial<MeetingNote>) =>
    api.post<MeetingNote>('/meetings', data),

  getMeetings: () =>
    api.get<MeetingNote[]>('/meetings'),

  getMeeting: (id: string) =>
    api.get<MeetingNote>(`/meetings/${id}`),

  updateMeeting: (id: string, data: Partial<MeetingNote>) =>
    api.put<MeetingNote>(`/meetings/${id}`, data),

  deleteMeeting: (id: string) =>
    api.delete(`/meetings/${id}`),

  uploadAudio: (meetingId: string, file: File) => {
    const formData = new FormData()
    formData.append('audio', file)
    return api.post<AudioProcessingResult>(`/meetings/${meetingId}/audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  generateSummary: (meetingId: string) =>
    api.post<{
      summary: string
      processAdjustments: string
      flavorOptimizations: string
    }>(`/meetings/${meetingId}/summary`),

  sendEmail: (meetingId: string) =>
    api.post<{ success: boolean; message: string }>(`/meetings/${meetingId}/email`),

  createExperimentRecord: (meetingId: string) =>
    api.post<{ recordId: string; markdown: string }>(`/meetings/${meetingId}/experiment-record`),

  updateTasteScore: (meetingId: string, score: TasteScore) =>
    api.put<MeetingNote>(`/meetings/${meetingId}/taste-score`, score),

  updateTissueParams: (meetingId: string, params: TissueEngineeringParams) =>
    api.put<MeetingNote>(`/meetings/${meetingId}/tissue-params`, params),
}

export default api
