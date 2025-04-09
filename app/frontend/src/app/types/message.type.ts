export enum MessageRole {
  User = 'USER',
  Assistant = 'ASSISTANT'
}

export interface Message {
  role: MessageRole;
  message: string;
}
