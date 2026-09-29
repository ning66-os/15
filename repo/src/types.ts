export interface TasteScore {
  juiciness: number
  tenderness: number
  elasticity: number
  flavor: number
  texture: number
  chewiness: number
}

export interface TissueEngineeringParams {
  cellDensity: number
  scaffoldPorosity: number
  fiberAlignment: number
  maturationRate: number
  extracellularMatrix: number
  vascularization: number
}

export interface Participant {
  id: string
  name: string
  role: 'scientist' | 'chef' | 'sensory' | 'pm'
  group: 'rd' | 'sensory'
}

export interface DiscussionSegment {
  id: string
  speaker: string
  group: string
  content: string
  timestamp: number
  duration: number
}

export interface MeetingNote {
  id: string
  title: string
  date: string
  participants: Participant[]
  tasteScore: TasteScore
  tissueParams: TissueEngineeringParams
  discussions: DiscussionSegment[]
  summary?: string
  processAdjustments?: string
  flavorOptimizations?: string
  experimentRecordId?: string
  emailSent?: boolean
  createdAt: string
}

export interface AudioProcessingResult {
  denoisedAudioPath: string
  transcript: string
  speakerSegments: {
    speaker: string
    start: number
    end: number
    text: string
    group: string
  }[]
}
