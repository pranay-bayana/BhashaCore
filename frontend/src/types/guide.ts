import { LanguageCode } from './api';

export type GuideCategory = 
  | 'getting_started'
  | 'languages'
  | 'rag_citations'
  | 'trial_accounts'
  | 'research'
  | 'limitations';

export interface GuideAction {
  type: 'navigate' | 'open_auth' | 'sample_query';
  target: string;
  label: Record<LanguageCode, string>;
}

export interface GuideTopic {
  id: string;
  category: GuideCategory;
  title: Record<LanguageCode, string>;
  question: Record<LanguageCode, string>;
  answer: Record<LanguageCode, string>;
  keywords: string[];
  action?: GuideAction;
}

export interface GuideMessage {
  id: string;
  sender: 'user' | 'guide';
  text: string;
  timestamp: number;
  action?: {
    type: 'navigate' | 'open_auth' | 'sample_query';
    target: string;
    label: string;
  };
}
