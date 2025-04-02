from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os
from typing import List, Dict

class RAGService:
    def __init__(self):
        # ใช้ all-MiniLM-L6-v2 สำหรับ embeddings (เล็กและเร็ว)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # สร้าง Chroma client
        self.vectorstore = Chroma(
            collection_name="notes_collection",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        # ใช้ facebook/opt-350m แทน (เป็น public model ที่เล็กกว่า)
        model_name = "facebook/opt-350m"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto"
        )
        
        # สร้าง pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=2048,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.15
        )
        
        # สร้าง LangChain LLM wrapper
        self.llm = HuggingFacePipeline(pipeline=pipe)
        
        # สร้าง conversation chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            ),
            return_source_documents=True,
            verbose=True
        )

    async def add_to_vectorstore(self, text: str, metadata: Dict) -> str:
        """เพิ่มข้อความเข้า vectorstore และคืนค่า embedding ID"""
        # แบ่งข้อความเป็น chunks
        chunks = self.text_splitter.split_text(text)
        
        # สร้าง metadata สำหรับแต่ละ chunk
        metadatas = [metadata for _ in chunks]
        
        # เพิ่มข้อมูลเข้า vectorstore
        ids = self.vectorstore.add_texts(
            texts=chunks,
            metadatas=metadatas
        )
        
        # คืนค่า embedding ID แรก (ใช้อ้างอิงทั้งชุด)
        return ids[0]

    async def search_similar(self, query: str, k: int = 3) -> List[Dict]:
        """ค้นหาข้อความที่คล้ายกับ query"""
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=k
        )
        
        return [{
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": score
        } for doc, score in results]

    async def ask_question(self, question: str, chat_history: List = []) -> Dict:
        """ถามคำถามโดยใช้ข้อมูลจาก vectorstore"""
        response = await self.qa_chain.ainvoke({
            "question": question,
            "chat_history": chat_history
        })
        
        return {
            "answer": response["answer"],
            "sources": [doc.metadata for doc in response["source_documents"]]
        }

    async def delete_embeddings(self, embedding_id: str):
        """ลบ embeddings ด้วย ID"""
        self.vectorstore.delete(ids=[embedding_id])

# สร้าง global instance
rag_service = RAGService()
