import { db } from '@/services/db';
import { urls } from '@/services/urls';

export interface Thread {
  created_date: string
  deleted: boolean
  id: string
  liked_by_current_user: boolean
  likes: number
  num_replies: number
  pinned: boolean
  post_id: string
  posted_by_current_user: boolean
  replied_to?: string | null
  text: string
  thread?: Array<Thread>
  user_id: string
  username: string
  depth?: number
}

export function setDepthOnThreads(threads: Array<Thread>, initialDepth: number): Array<Thread> {
  threads.forEach((thread) => {
    if (!thread) {
      console.log(thread, 'no thread!')
    }
    thread.depth = initialDepth // Assign current depth

    if (thread.thread && thread.thread.length) {
      // Check if there are subthreads
      setDepthOnThreads(thread.thread, initialDepth + 1) // Pass incremented depth for subthreads
    }
  })

  return threads // Return modified threads after processing
}

export function flattenThreads(threads: Array<Thread>): Array<Thread> {
  return threads.reduce(
    (flattened: Thread[], thread) => [
      ...flattened,
      thread,
      ...(thread.thread?.length ? flattenThreads(thread.thread) : []),
    ],
    []
  )
}

export type PostResponse = {
  posts: {
    id: string
    [key: string]: any
  }
}

export async function likeThread(thread: Thread) {
  await db.post(urls.reviews.likeComment(thread.id), false, null, (res:any) => {
    thread.num_replies += 1;
  }, (err:any) => {
    console.warn(err, 'something weird happened');
  });
};
