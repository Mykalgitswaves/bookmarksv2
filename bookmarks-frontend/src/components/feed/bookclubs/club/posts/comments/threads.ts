import { db } from '@/services/db';
import { urls } from '@/services/urls';
import { defineEmits } from 'vue';

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
  depth: number
  replies?: Array<Thread>
}


// Flatten, if there is a max depth then reduce until that depth is hit. 
export function flattenThreads(threads: Array<Thread>, maxDepth: number): Array<Thread> {
  // otherwise flatten them recursively. 
  const flattened: Set<Thread> = new Set();
  
  function walkThreads(threads: Array<Thread>) {
    for (const thread of threads) {
      if (thread.depth > maxDepth) {
        break;
      };
      
      // Add depth property to the thread
      flattened.add(thread);

      // If we haven't reached max depth and there are child threads, process them
      if (thread.depth < maxDepth && thread.thread && thread.thread.length > 0) {
        walkThreads(thread.thread);
      }
    }
  }
  
  // Start the recursive walk
  walkThreads(threads);

  console.log(flattened);

  // Convert Set back to Array before returning
  return Array.from(flattened);
}

export interface PostResponse {
  posts: {
    id: string;
    [key: string]: any;
  }
}

export interface CommentPayload {
  commentId: string;
  reply: string;
}

const ERROR_lOG = 'something weird happened: ';

export async function likeThread(thread: Thread) {
  await db.put(urls.reviews.likeComment(thread.id), 
    null, 
    false, 
    (res: any) => {
      console.log(res, 'what?');
      thread.likes += 1;
      thread.liked_by_current_user = true;
    },
    (err: any) => {
      console.warn(ERROR_lOG, err);
    }
  );
};

export async function unlikeThread(thread: Thread) {
  await db.put(urls.reviews.unlikeComment(thread.id), 
    null, 
    false,
    (res: any) => {
      thread.likes -= 1;
      thread.liked_by_current_user = false;
    },
    (err: any) => {
      console.warn(ERROR_lOG, err);
    }
  )
}

const emit = defineEmits();

export async function deleteThread(thread: Thread) {
  await db.put(urls.reviews.deleteComment(thread.id),
  null, 
  false,
  (res: any) => {
    thread.deleted = true;
    emit('deleted-thread', thread);
  },
  (err: any) => {
    console.warn(ERROR_lOG, err)
  }
  )
}